#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OneBox Report Uploader for MR Reviewer

此脚本用于将生成的MR检视报告上传到OneBox指定目录，并生成全员可访问的分享链接
上传成功后自动更新mr_coordinator.json中的risk_level和report_share_url字段

Usage:
    python upload_report_to_onebox.py --repo "{repo}" --mrId {mrId}
"""

import argparse
import base64
import json
import platform
import sys
import os
import re
import shutil
import time
import traceback
from pathlib import Path
from datetime import datetime
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

scripts_dir = Path(__file__).parent.parent
sys.path.insert(0, str(scripts_dir))

from onebox.onebox_engine import OneBoxEngine
sys.path.insert(0, str(scripts_dir / 'common'))
from logger_manager import get_logger


# ======================== 凭据读取 ========================

CAC_CREDENTIALS_FILE = Path("~/.cac/.credentials.json").expanduser()


def _is_expired(expires_at_ms: int) -> bool:
    """检查毫秒级时间戳是否已过期"""
    import time as _time
    return _time.time() * 1000 > expires_at_ms


def _decrypt_dpapi(raw_b64: str) -> str:
    """Windows DPAPI 解密 Base64 编码的数据

    :param raw_b64: Base64 编码的 DPAPI 加密数据
    :return: 解密后的明文字符串
    """
    encrypted = base64.b64decode(raw_b64)
    if platform.system() == "Windows":
        import win32crypt
        _, decrypted = win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)
        return decrypted.decode("utf-8")
    else:
        return encrypted.decode("utf-8")


def _try_get_cookies_from_credentials() -> dict | None:
    """尝试从 ~/.cac/.credentials.json 读取并解密 SSO cookies

    读取 idaasOAuth.cookies 字段（Windows 下 DPAPI 加密，Linux 下明文 JSON），
    解密后返回 cookies 字典。

    Returns:
        cookies 字典 (如 {"hwssot": "...", "hwsso_login": "...", "login_uid": "..."})
        或 None（文件不存在 / 格式错误 / 已过期 / 解密失败）
    """
    if not CAC_CREDENTIALS_FILE.exists():
        print("[INFO] 凭据文件不存在，跳过 cookies 方式")
        return None

    try:
        with open(CAC_CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            cred_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[WARN] 读取凭据文件失败: {e}")
        return None

    # 读取 idaasOAuth.cookies
    try:
        idaas = cred_data["idaasOAuth"]
        raw_cookies = idaas.get("cookies", "")
        if not raw_cookies:
            print("[INFO] credentials.json 中无 cookies 字段")
            return None
    except (KeyError, TypeError):
        print("[INFO] credentials.json 中无 idaasOAuth.cookies")
        return None

    # 检查 cookies 过期时间
    cookie_expires = idaas.get("cookieExpires", 0)
    if cookie_expires and _is_expired(cookie_expires):
        print(f"[WARN] credentials.json 中 cookies 已过期 (cookieExpires={cookie_expires})")
        return None

    # 解密 cookies
    try:
        cookie_str = _decrypt_dpapi(raw_cookies)
        cookies_dict = json.loads(cookie_str)
    except Exception as e:
        print(f"[WARN] cookies 解密或解析失败: {e}")
        return None

    # 验证最小必需字段
    required_keys = {"hwssot", "hwsso_login", "login_uid"}
    if not required_keys.issubset(cookies_dict.keys()):
        missing = required_keys - set(cookies_dict.keys())
        print(f"[WARN] cookies 缺少必需字段: {missing}")
        return None

    print(f"[INFO] 从 credentials.json 读取 SSO cookies 成功 (字段: {list(cookies_dict.keys())})")
    return cookies_dict


TYPE_PREFIX_MAP = {
    'coordinator': 'mr_coordinator',
    'analysis_stage0': 'analysis_stage0',
    'analysis_stage1': 'analysis_stage1',
    'analysis_stage2': 'analysis_stage2',
    'mr_risks': 'mr_risks',
}

REPORT_VALID_RISK_LEVELS = {'high', 'medium', 'low'}


def get_temp_file_path(file_type, repo, mr_id):
    """计算临时文件路径"""
    temp_dir = Path.home() / ".mr-reviewer" / "temp"
    safe_repo_name = repo.replace('/', '_')
    prefix = TYPE_PREFIX_MAP.get(file_type, file_type)
    mr_subdir = temp_dir / f"mr_{safe_repo_name}_{mr_id}"
    mr_subdir.mkdir(parents=True, exist_ok=True)
    return mr_subdir / f"{prefix}.json"


def normalize_risk_level(risk_level: str) -> str:
    """规范化风险等级"""
    if not risk_level:
        return ''
    mapping = {'高': 'high', '中': 'medium', '低': 'low'}
    for k, v in mapping.items():
        if k in risk_level:
            return v
    return risk_level if risk_level in REPORT_VALID_RISK_LEVELS else ''


def get_report_path(repo: str, mr_id: str) -> tuple:
    """计算报告文件路径，扫描目录下mr_review_report_*.md文件"""
    mr_info_file = get_temp_file_path('coordinator', repo, mr_id)
    if not mr_info_file.exists():
        raise FileNotFoundError(f"coordinator文件不存在: {mr_info_file}")

    mr_subdir = mr_info_file.parent
    report_files = list(mr_subdir.glob("mr_review_report_*.md"))
    if not report_files:
        raise FileNotFoundError(f"未找到报告文件: {mr_subdir}/mr_review_report_*.md")
    if len(report_files) > 1:
        print(f"[WARN] 找到多个报告文件，使用最新修改的: {report_files[-1]}")
    report_path = report_files[-1]

    risk_level = ''
    filename = report_path.stem
    for lvl in REPORT_VALID_RISK_LEVELS:
        if filename.endswith(f"_{lvl}"):
            risk_level = lvl
            break

    return report_path, risk_level


class OneBoxReportUploader:
    """OneBox报告上传器"""

    def __init__(self, config_path=None, repo=None, mr_id=None):
        self.config_path = config_path
        self.config = self._load_config()
        self.repo = repo
        self.mr_id = mr_id

    def _load_config(self):
        """加载配置文件"""
        if self.config_path:
            if isinstance(self.config_path, str):
                self.config_path = Path(self.config_path)

            if not self.config_path.exists():
                print(f"[ERROR] 配置文件不存在: {self.config_path}")
                return None

            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ERROR] 加载配置文件失败: {e}")
                return None
        else:
            # 尝试从默认位置加载
            default_paths = [
                Path.home() / ".mr-reviewer" / "config.json",
                Path(__file__).parent.parent.parent / "config.json"
            ]
            for path in default_paths:
                if path.exists():
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            return json.load(f)
                    except Exception as e:
                        print(f"[WARN] 加载配置文件失败 {path}: {e}")
            return None

    def parse_onebox_directory_url(self, url):
        """
        解析OneBox目录URL，提取parent_id

        Args:
            url: OneBox目录URL，格式如：https://onebox.huawei.com/#file/1/82547

        Returns:
            str: parent_id，解析失败返回None
        """
        if not url:
            return None

        # 解析URL格式：https://onebox.huawei.com/#file/1/82547
        match = re.search(r'/#file/1/(\d+)', url)
        if match:
            return match.group(1)

        print(f"[WARN] 无法解析OneBox目录URL: {url}")
        return None

    def _prepare_date_folder(self, report_path, now):
        """
        在本地准备日期目录结构，并返回日期目录路径

        Args:
            report_path: 报告文件路径
            now: 当前时间datetime对象

        Returns:
            Path: 日期目录路径，失败返回None
        """
        try:
            # 获取当前日期
            year = now.strftime("%Y")
            month = now.strftime("%m")
            day = now.strftime("%d")

            print(f"[INFO] 当前日期: {year}-{month}-{day}")

            # 获取报告文件所在目录
            report_file = Path(report_path)
            output_dir = report_file.parent

            # 创建日期目录结构
            date_dir = output_dir / year / month / day
            date_dir.mkdir(parents=True, exist_ok=True)

            # 复制报告文件到日期目录
            target_file = date_dir / report_file.name
            shutil.copy2(report_path, target_file)

            print(f"[SUCCESS] 日期目录已准备: {date_dir}")
            print(f"[SUCCESS] 报告文件已复制到: {target_file}")

            # 返回包含年份目录的路径
            return output_dir / year

        except Exception as e:
            print(f"[ERROR] 准备日期目录失败: {e}")
            traceback.print_exc()
            return None

    def _find_or_create_date_folder_in_onebox(self, engine, root_file_list, root_parent_id, year, month, day):
        """
        在OneBox中查找或创建日期目录结构

        Args:
            engine: OneBoxEngine实例
            root_file_list: 根目录文件列表（已缓存）
            root_parent_id: 根目录ID
            year: 年份
            month: 月份
            day: 日期

        Returns:
            int: 日期目录ID，失败返回None
        """
        try:
            # 从根目录列表中查找年目录
            print(f"[DEBUG] 从根目录列表查找年目录: {year}")
            year_folder = next((f for f in root_file_list if f.get('name') == year and f.get('type') == 0), None)
            if not year_folder:
                print(f"[DEBUG] 根目录列表中未找到年目录: {year}，尝试创建")
                year_folder_id = self._create_folder_by_name(engine, root_parent_id, year)
                if not year_folder_id:
                    return None
                year_folder = {'id': year_folder_id, 'name': year}
                print(f"[DEBUG] 年目录创建成功: {year_folder}")
            else:
                print(f"[DEBUG] 找到年目录: {year_folder}")

            # 查找月目录（需要新查询）
            year_space_url = f"https://onebox.huawei.com/#file/1/{year_folder['id']}"
            print(f"[DEBUG] 查找月目录: {month}")
            month_folder = self._find_folder_by_name(engine, year_space_url, month)
            if not month_folder:
                print(f"[DEBUG] 未找到月目录: {month}，尝试创建")
                month_folder_id = self._create_folder_by_name(engine, year_folder['id'], month)
                if not month_folder_id:
                    return None
                month_folder = {'id': month_folder_id, 'name': month}
                print(f"[DEBUG] 月目录创建成功: {month_folder}")
            else:
                print(f"[DEBUG] 找到月目录: {month_folder}")

            # 查找日目录（需要新查询）
            month_space_url = f"https://onebox.huawei.com/#file/1/{month_folder['id']}"
            print(f"[DEBUG] 查找日目录: {day}")
            day_folder = self._find_folder_by_name(engine, month_space_url, day)

            if not day_folder:
                print(f"[DEBUG] 未找到日目录: {day}，尝试创建")
                day_folder_id = self._create_folder_by_name(engine, month_folder['id'], day)
                if not day_folder_id:
                    return None
                day_folder = {'id': day_folder_id, 'name': day}
                print(f"[DEBUG] 日目录创建成功: {day_folder}")
            else:
                print(f"[DEBUG] 找到日目录: {day_folder}")

            return day_folder['id']

        except Exception as e:
            print(f"[ERROR] 查找或创建日期目录失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _find_folder_by_name(self, engine, space_url, folder_name):
        """
        在指定目录中查找同名文件夹

        Args:
            engine: OneBoxEngine实例
            space_url: 父目录URL
            folder_name: 文件夹名称

        Returns:
            dict: 文件夹信息，未找到返回None
        """
        try:
            file_list = engine.list_folder(space_url)
            print(f"[DEBUG] 列出目录内容: {space_url}")
            print(f"[DEBUG] 文件列表: {file_list}")

            if file_list:
                for file in file_list:
                    print(f"[DEBUG] 检查文件: {file.get('name')}, 类型: {file.get('type')}")
                    if file.get('name') == folder_name and file.get('type') == 0:
                        return file
            return None
        except Exception as e:
            print(f"[ERROR] 创建文件夹失败: {e}")
            traceback.print_exc()
            return None

    def _create_folder_by_name(self, engine, parent_id, folder_name):
        """
        在指定目录中创建文件夹

        Args:
            engine: OneBoxEngine实例
            parent_id: 父目录ID
            folder_name: 文件夹名称

        Returns:
            int: 文件夹ID，失败返回None
        """
        try:
            space_url = f"https://onebox.huawei.com/#file/1/{parent_id}"
            folder_id = engine.create_folder(space_url, folder_name)
            return folder_id
        except Exception as e:
            print(f"[ERROR] 创建文件夹失败: {e}")
            return None

    def _find_file_recursive(self, engine, space_url, file_name, file_list):
        """
        递归查找文件

        Args:
            engine: OneBoxEngine实例
            space_url: 当前目录URL
            file_name: 要查找的文件名
            file_list: 当前目录的文件列表

        Returns:
            int: 文件ID，未找到返回None
        """
        for file in file_list:
            if file.get('name') == file_name and file.get('type') != 0:
                return file.get('id')
            elif file.get('type') == 0:
                sub_space_url = f"https://onebox.huawei.com/#file/1/{file.get('id')}"
                sub_file_list = engine.list_folder(sub_space_url)
                result = self._find_file_recursive(engine, sub_space_url, file_name, sub_file_list)
                if result:
                    return result
        return None

    def upload_report(self, report_path):
        """
        上传报告到OneBox并生成分享链接

        Args:
            report_path: 报告文件路径

        Returns:
            tuple: (success: bool, share_url: str, message: str)
        """
        safe_repo_name = self.repo or "unknown"
        mr_id = self.mr_id or "unknown"
        mr_info = f"{safe_repo_name}_{mr_id}"
        logger = get_logger(mr_info)

        logger.info(f"开始 - 上传报告到OneBox")
        start_time = datetime.now()

        if not self.config:
            logger.error(f"配置未加载")
            return False, None, "配置未加载"

        onebox_share_directory_url = self.config.get("onebox_share_directory_url", "")
        if not onebox_share_directory_url:
            print("[WARN] 未配置onebox_share_directory_url，跳过上传")
            logger.info(f"跳过 - 未配置onebox_share_directory_url")
            return False, None, "未配置onebox_share_directory_url"

        root_parent_id = self.parse_onebox_directory_url(onebox_share_directory_url)
        if not root_parent_id:
            logger.error(f"无法解析OneBox目录URL")
            return False, None, "无法解析OneBox目录URL"

        print(f"[INFO] OneBox分享目录URL: {onebox_share_directory_url}")
        print(f"[INFO] 根目录parent_id: {root_parent_id}")

        if not Path(report_path).exists():
            logger.error(f"报告文件不存在: {report_path}")
            return False, None, f"报告文件不存在: {report_path}"

        # ---------- 优先级1: 从 credentials.json 读取 SSO cookies ----------
        cookies_dict = _try_get_cookies_from_credentials()

        try:
            if cookies_dict:
                print(f"[INFO] 正在使用 SSO cookies 登录 (来自 ~/.cac/.credentials.json)")
                logger.info(f"开始登录OneBox - 方式: SSO cookies")
                engine = OneBoxEngine(cookies_dict=cookies_dict)
                logger.info(f"登录OneBox成功 (cookies方式)")
            else:
                # ---------- 优先级2: 使用 config.json 中的 username/password ----------
                username = self.config.get("onebox_username", "")
                password = self.config.get("onebox_password", "")
                idss_cid = self.config.get("onebox_idss_cid", "")

                if not username or not password:
                    logger.error(f"配置中缺少onebox_username或onebox_password，且 credentials.json 中无可用 cookies")
                    return False, None, "配置中缺少onebox_username或onebox_password，且 credentials.json 中无可用 cookies"

                print(f"[INFO] 正在使用用户名登录: {username}")
                logger.info(f"开始登录OneBox - 方式: 用户名密码, 用户名: {username}")
                engine = OneBoxEngine(
                    username=username,
                    password=password,
                    idss_cid=idss_cid
                )
                logger.info(f"登录OneBox成功 (用户名密码方式)")

            root_space_url = f"https://onebox.huawei.com/#file/1/{root_parent_id}"
            print(f"[INFO] 根空间URL: {root_space_url}")

            print(f"[INFO] 正在获取根空间信息...")
            space_info = engine.get_space_info(root_space_url)

            if not space_info:
                logger.error(f"获取根空间信息失败")
                return False, None, "获取根空间信息失败"

            logger.info(f"获取根空间信息成功 - owner_id: {space_info.get('owner_id')}, parent_id: {space_info.get('parent_id')}")

            print(f"[INFO] 正在获取根目录文件列表...")
            root_file_list = engine.list_folder(root_space_url)
            if root_file_list is None:
                logger.error(f"无法获取根目录文件列表")
                return False, None, "无法获取根目录文件列表"
            print(f"[INFO] 根目录文件列表: {root_file_list}")

            owner_id = space_info.get('owner_id')
            if owner_id:
                print(f"[INFO] owner_id: {owner_id}")
            else:
                owner_id = root_file_list[0].get('owner_id')
                if owner_id:
                    print(f"[INFO] owner_id: {owner_id}")
                else:
                    logger.error(f"无法获取owner_id")
                    return False, None, "无法获取owner_id"

            now = datetime.now()
            year = now.strftime("%Y")
            month = now.strftime("%m")
            day = now.strftime("%d")

            print(f"[INFO] 正在上传报告到OneBox: {year}/{month}/{day}")
            logger.info(f"上传报告到OneBox - 日期路径: {year}/{month}/{day}")
            
            # 使用预上传API，直接上传文件到路径 {year}/{month}/{day}/{file_name}
            # OneBox会自动创建目录结构
            print(f"[INFO] 正在使用预上传API上传文件...")
            
            # 读取文件内容
            with open(report_path, 'rb') as f:
                file_data = f.read()
            
            file_name = Path(report_path).name
            
            # 使用预上传API，路径为 {year}/{month}/{day}/{file_name}
            folder_path = f"{year}/{month}/{day}"
            upload_file_name = f"{folder_path}/{file_name}"
            
            print(f"[INFO] 上传路径: {upload_file_name}, 文件大小: {len(file_data)}字节")
            logger.info(f"预上传 - owner_id: {owner_id}, parent_id: {root_parent_id}, 上传路径: {upload_file_name}, 文件大小: {len(file_data)}字节")

            # 预上传 - 直接获取 file_id，无需递归搜索
            upload_url, file_id = engine.perfect_files_pre_upload(
                owner_id=owner_id,
                parent_id=int(root_parent_id),
                file_name=upload_file_name,
                file_size=len(file_data),
            )
            print(f"[INFO] 预上传成功，file_id: {file_id}")
            logger.info(f"预上传成功 - upload_url: {upload_url[:80]}..., file_id: {file_id}")

            engine.upload(upload_url=upload_url, file_name=file_name, file_data=file_data)
            print(f"[SUCCESS] 报告文件上传成功！")
            logger.info(f"报告文件上传到OneBox成功 - {upload_file_name}")

            print(f"[INFO] 文件ID: {file_id} (直接使用预上传返回的file_id，无需递归搜索)")

            print(f"[INFO] 正在获取分享链接...")
            logger.info(f"获取分享链接 - file_id: {file_id}, owner_id: {owner_id}")
            share_url = engine.perfect_template_get_invitation_url(file_id=file_id, owner_id=owner_id)
            print(f"[INFO] 分享链接: {share_url}")
            logger.info(f"获取分享链接成功 - share_url: {share_url}")

            link_code = share_url.split('/')[-1].split('?')[0]
            print(f"[INFO] link_code: {link_code}")
            logger.info(f"设置分享权限 - link_code: {link_code}, link_role: viewer")

            print(f"[INFO] 正在设置分享权限为: viewer（可预览/下载）")
            logger.info(f"设置分享权限")
            engine.perfect_invite_edit_new_all_share(
                owner_id=owner_id,
                file_id=file_id,
                link_code=link_code,
                link_role=OneBoxEngine.LinkRole.viewer
            )
            print(f"[SUCCESS] 分享权限设置成功！")
            logger.info(f"分享权限设置成功 - link_code: {link_code}")

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"完成 - 分享链接: {share_url} (耗时: {duration:.2f}秒)")

            return True, share_url, "上传成功并生成分享链接"

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            print(f"[ERROR] 上传失败: {e}")
            traceback.print_exc()
            logger.error(f"失败 - {e} (耗时: {duration:.2f}秒)")
            return False, None, f"上传失败: {e}"

    def run(self, report_path):
        """
        执行上传流程

        Args:
            report_path: 报告文件路径

        Returns:
            tuple: (success: bool, share_url: str, message: str)
        """
        return self.upload_report(report_path)


def main():
    parser = argparse.ArgumentParser(description='上传MR检视报告到OneBox并生成分享链接')
    parser.add_argument('--repo', required=True, help='仓库名称')
    parser.add_argument('--mrId', required=True, help='MR ID')

    args = parser.parse_args()

    report_path, risk_level = get_report_path(args.repo, args.mrId)
    print(f"[INFO] 自动计算报告路径: {report_path}")
    print(f"[INFO] 解析风险等级: {risk_level or '未识别'}")

    safe_repo_name = args.repo.replace('/', '_')
    logger = get_logger(f"{safe_repo_name}_{args.mrId}")
    logger.info(f"报告路径: {report_path}, 风险等级: {risk_level or '未识别'}")

    # 上传报告前，先回填 risk_level 到 coordinator
    if risk_level:
        update_coordinator_risk_level(args.repo, args.mrId, risk_level)
    else:
        # 如果从文件名解析不到，尝试从 analysis_stage2.json 读取
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / 'common'))
            from generate_report_filename import get_risk_level_from_analysis_stage2
            coordinator_dir = get_temp_file_path('coordinator', args.repo, args.mrId).parent
            risk_level = get_risk_level_from_analysis_stage2(coordinator_dir)
            if risk_level:
                update_coordinator_risk_level(args.repo, args.mrId, risk_level)
            else:
                logger.warning(f"未找到有效风险等级，跳过 risk_level 回填")
        except Exception as e:
            logger.warning(f"尝试从 analysis_stage2.json 读取 risk_level 失败: {e}")

    uploader = OneBoxReportUploader(repo=args.repo, mr_id=args.mrId)
    success, share_url, message = uploader.run(report_path)

    if success:
        print(f"[SUCCESS] {message}")
        print(f"[INFO] 分享链接: {share_url}")

        # 上传成功后，回填 report_share_url 到 coordinator
        update_coordinator_share_url(args.repo, args.mrId, share_url)

        sys.exit(0)
    else:
        print(f"[ERROR] {message}")
        sys.exit(1)


def update_coordinator_risk_level(repo: str, mr_id: str, risk_level: str):
    """只更新mr_coordinator.json中的risk_level（上传报告前调用）"""
    coordinator_path = get_temp_file_path('coordinator', repo, mr_id)
    safe_repo_name = repo.replace('/', '_')
    logger = get_logger(f"{safe_repo_name}_{mr_id}")
    logger.info(f"更新coordinator risk_level - 路径: {coordinator_path}, risk_level: {risk_level}")
    try:
        with open(coordinator_path, 'r', encoding='utf-8') as f:
            coordinator_data = json.load(f)

        coordinator_data['risk_level'] = risk_level

        with open(coordinator_path, 'w', encoding='utf-8') as f:
            json.dump(coordinator_data, f, ensure_ascii=False, indent=2)

        print(f"[INFO] 已更新coordinator risk_level: {risk_level}")
        logger.info(f"更新coordinator risk_level成功: {risk_level}")
    except Exception as e:
        print(f"[ERROR] 更新coordinator risk_level失败: {e}")
        logger.error(f"更新coordinator risk_level失败 - {e}")


def update_coordinator_share_url(repo: str, mr_id: str, share_url: str):
    """只更新mr_coordinator.json中的report_share_url（上传报告成功后调用）"""
    coordinator_path = get_temp_file_path('coordinator', repo, mr_id)
    safe_repo_name = repo.replace('/', '_')
    logger = get_logger(f"{safe_repo_name}_{mr_id}")
    logger.info(f"更新coordinator report_share_url - 路径: {coordinator_path}, share_url: {share_url}")
    try:
        with open(coordinator_path, 'r', encoding='utf-8') as f:
            coordinator_data = json.load(f)

        coordinator_data['report_share_url'] = share_url

        with open(coordinator_path, 'w', encoding='utf-8') as f:
            json.dump(coordinator_data, f, ensure_ascii=False, indent=2)

        print(f"[INFO] 已更新coordinator report_share_url: {share_url}")
        logger.info(f"更新coordinator report_share_url成功: {share_url}")
    except Exception as e:
        print(f"[ERROR] 更新coordinator report_share_url失败: {e}")
        logger.error(f"更新coordinator report_share_url失败 - {e}")


if __name__ == '__main__':
    main()
