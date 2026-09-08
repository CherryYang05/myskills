#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OneBox API Engine for MR Reviewer
"""

import enum
import http
import os
import re
import requests
import requests_toolbelt
import urllib.parse


class OneBoxEngine:
    """OneBox API引擎"""

    class LinkRole(enum.Enum):
        onlineViewer = "onlineViewer"  # 可预览/不可复制内容
        previewer = "previewer"  # 可预览
        online_editor = "online_editor"  # 可编辑
        viewer = "viewer"  # 可预览/下载
        online_operator = "online_operator"  # 可编辑/下载

    def __init__(self, username: str = "", password: str = "", idss_cid: str = "",
                 cookies_dict: dict = None):
        """
        :param username: w3 用户名
                    格式: a00123456
        :param password: w3 密码
        :param idss_cid: idss_cid
                获取方式: 登录w3 -> F12 -> 网络/Network -> 搜索 "idss_cid"
                必要性: Windows 可填，Linux 必填
        :param cookies_dict: SSO cookies 字典 (优先级高于 username/password)
                    从 ~/.cac/.credentials.json 的 idaasOAuth.cookies 解密得到
                    最小必需: {"hwssot": "...", "hwsso_login": "...", "login_uid": "..."}
        """

        self.username = username
        self.password = password
        self.idss_cid = idss_cid
        self._cached_owner_id = None  # 缓存owner_id，避免重复请求

        # 优先使用 cookies_dict，否则用 username/password 登录获取
        if cookies_dict:
            self.cookies = self._build_cookie_jar(cookies_dict)
        else:
            self.cookies = self.get_cookies()

        self.csrf_token = self.get_csrf_token()

        self.json_headers = {
            "Csrftoken": self.csrf_token,
        }

        self.urlencoded_payload_headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Csrftoken": self.csrf_token,
        }

    @staticmethod
    def _build_cookie_jar(cookies_dict: dict) -> requests.cookies.RequestsCookieJar:
        """从 cookies 字典构建 RequestsCookieJar

        :param cookies_dict: SSO cookies 字典，如 {"hwssot": "...", "hwsso_login": "...", "login_uid": "..."}
        :return: requests.cookies.RequestsCookieJar
        """
        jar = requests.cookies.RequestsCookieJar()
        for k, v in cookies_dict.items():
            jar.set(k, str(v), domain=".huawei.com", path="/")
        return jar

    @staticmethod
    def _safe_join(folder_path: str, file_name: str) -> str:
        """
        安全地拼接文件夹路径和文件名，防止路径遍历攻击。

        :param folder_path: 基准文件夹路径
        :param file_name: 文件名（可能包含路径）
        :return: 安全拼接后的绝对路径
        :raises ValueError: 当文件路径试图跳出基准目录时
        """
        folder_path = os.path.realpath(folder_path)
        final_path = os.path.realpath(os.path.join(folder_path, file_name))
        if os.name == 'nt':
            folder_path = folder_path.lower()
            final_path = final_path.lower()
        if not final_path.startswith(folder_path + os.sep) and final_path != folder_path:
            raise ValueError(f"非法路径 traversal 检测: {file_name}")
        return final_path

    @staticmethod
    def _safe_makedirs(folder_path: str, relative_path: str) -> str:
        """
        安全地创建子目录，防止路径遍历攻击。

        :param folder_path: 基准文件夹路径
        :param relative_path: 相对路径（可能包含多级子目录）
        :return: 安全拼接后的绝对路径
        :raises ValueError: 当路径试图跳出基准目录时
        """
        folder_path = os.path.realpath(folder_path)
        final_path = os.path.realpath(os.path.join(folder_path, relative_path))
        if os.name == 'nt':
            folder_path = folder_path.lower()
            final_path = final_path.lower()
        if not final_path.startswith(folder_path + os.sep) and final_path != folder_path:
            raise ValueError(f"非法路径 traversal 检测: {relative_path}")
        os.makedirs(final_path, exist_ok=True)
        return final_path

    def get_cookies(self) -> requests.cookies.RequestsCookieJar:
        response = requests.request(
            method="POST",
            url="https://login.huawei.com/login1/rest/hwidcenter/login",
            json={
                "uid": self.username,
                "password": self.password,
                "fingerPrint": {
                    "cid": self.idss_cid,
                },
            },
            headers={
                "User-Agent": "Mozilla",
            },
        )
        return response.cookies

    def get_csrf_token(self) -> str:
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/login/authforword",
            cookies=self.cookies,
            allow_redirects=False,
        )
        
        # 检查响应状态
        if response.status_code != 302:
            raise Exception(f"获取CSRF token失败，状态码: {response.status_code}，期望302")
        
        # 检查Set-Cookie头
        if "Set-Cookie" not in response.headers:
            raise Exception(f"获取CSRF token失败，响应中没有Set-Cookie头。响应头: {response.headers}")
        
        # 提取CSRF token
        regex_result = re.search(pattern="WAPCSRFTOKEN=(\S+?);", string=response.headers["Set-Cookie"])
        if not regex_result:
            raise Exception(f"获取CSRF token失败，无法从Set-Cookie中提取。Set-Cookie: {response.headers['Set-Cookie']}")
        
        csrf_token = regex_result.group(1)
        return csrf_token

    def get_owner_id(self) -> int:
        """获取owner_id，使用缓存避免重复请求"""
        if self._cached_owner_id is not None:
            return self._cached_owner_id

        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/user/accountinfo",
            headers=self.json_headers,
            cookies=self.cookies,
        )
        data = response.json().get("data", {})
        owner_id = data.get("ownerId")
        if owner_id is None:
            # 尝试其他可能的字段名
            owner_id = data.get("owner_id")
        if owner_id is None:
            # 尝试使用id字段
            owner_id = data.get("id")
        if owner_id is None:
            raise ValueError(f"无法获取owner_id，响应: {response.text}")

        self._cached_owner_id = int(owner_id)
        return self._cached_owner_id

    def get_space_info(self, space_url: str) -> dict:
        """
        获取空间信息

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :return: 空间信息
        """

        # 解析空间URL
        # 格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        # 或: https://onebox.huawei.com/#file/1/<parent_id>

        # 提取parent_id
        if "/#file/1/" in space_url:
            parent_id = space_url.split("/#file/1/")[1]
            owner_id = self.get_owner_id()
        else:
            parts = space_url.split("/")
            parent_id = parts[-2]
            owner_id = int(parts[-1])

        return {
            "owner_id": owner_id,
            "parent_id": parent_id,
        }

    def perfect_files_list_attribute(self, owner_id: int, file_id: int) -> dict:
        """
        [API] 获取文件属性

        :param owner_id:
        :param file_id:
        :return:
        """

        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/files/listAttribute/%d/%d" % (owner_id, file_id),
            headers=self.json_headers,
            cookies=self.cookies,
        )
        return response.json()["data"]

    def perfect_folders_list(self, owner_id: int, parent_id: int) -> list:
        """
        [API] 单层列举文件夹

        :param owner_id:
        :param parent_id:
        :return:
        """
        PAGE_SIZE = 1000
        payload = {
            "ownerId": owner_id,
            "parentId": parent_id,
            "pageNumber": 1,
            "pageSize": PAGE_SIZE,
            "orderField": "name",
            "desc": "false",
            "token": "",
            "mode": "",
        }
        perfect_folders_list_api = "https://onebox.huawei.com/perfect/folders/list"
        response = requests.request(
            method="POST",
            url=perfect_folders_list_api,
            headers=self.urlencoded_payload_headers,
            data=urllib.parse.urlencode(query=payload),
            cookies=self.cookies,
        )
        page_num = response.json()["data"]["totalPages"]
        file_list = []
        # noinspection PyTypeChecker
        for i in range(page_num):
            payload = {
                "ownerId": owner_id,
                "parentId": parent_id,
                "pageNumber": i + 1,
                "pageSize": PAGE_SIZE,
                "orderField": "name",
                "desc": "false",
                "token": "",
                "mode": "",
            }
            response = requests.request(
                method="POST",
                url=perfect_folders_list_api,
                headers=self.urlencoded_payload_headers,
                data=urllib.parse.urlencode(query=payload),
                cookies=self.cookies,
            )
            file_list.extend(response.json()["data"]["content"])
        return file_list

    def list_folder(self, space_url: str) -> list:
        """
        单层遍历文件夹

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :return:
        """
        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]
        parent_id = space_info["parent_id"]
        return self.perfect_folders_list(owner_id=owner_id, parent_id=parent_id)

    def list_folder_recursive(self, space_url: str) -> list:
        """
        递归遍历文件夹

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :return:
        """
        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]
        parent_id = space_info["parent_id"]

        # 广度优先搜索
        file_list = []
        queue = [{"parent_id": parent_id, "path": ""}]

        while len(queue) > 0:
            current = queue.pop(0)
            current_parent_id = current["parent_id"]
            current_path = current["path"]

            files = self.perfect_folders_list(owner_id=owner_id, parent_id=current_parent_id)
            for file in files:
                file_path = os.path.join(current_path, file["name"])
                file["path"] = file_path
                file_list.append(file)

                if file["type"] == "folder":
                    queue.append({
                        "parent_id": file["id"],
                        "path": file_path
                    })

        return file_list

    def perfect_files_pre_upload(self, owner_id: int, parent_id: int, file_name: str, file_size: int) -> tuple:
        """
        [API] 预上传

        :param owner_id:
        :param parent_id:
        :param file_name:
        :param file_size:
        :return: tuple (upload_url, file_id)
            - upload_url: 用于上传文件的URL
            - file_id: 文件ID，可直接用于获取分享链接，无需递归搜索
        """

        payload = {
            "ownerId": owner_id,
            "parentId": parent_id,
            "name": file_name,
            "size": file_size,
        }

        perfect_files_pre_upload_api = "https://onebox.huawei.com/uploadFolder/dirPreupload"
        response = requests.request(
            method="POST",
            url=perfect_files_pre_upload_api,
            headers=self.urlencoded_payload_headers,
            data=urllib.parse.urlencode(query=payload),
            cookies=self.cookies,
        )

        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"preUpload请求失败，状态码: {response.status_code}, 响应内容: {response.text}")

        # 检查响应结构
        try:
            response_json = response.json()
        except Exception as e:
            raise Exception(f"preUpload响应不是有效的JSON格式。响应内容: {response.text}, 错误: {e}")

        if "data" not in response_json:
            raise Exception(f"preUpload响应缺少data字段。响应内容: {response_json}")

        if "uploadUrl" not in response_json["data"]:
            raise Exception(f"preUpload响应缺少uploadUrl字段。响应内容: {response_json}")

        if "fileId" not in response_json["data"]:
            raise Exception(f"preUpload响应缺少fileId字段。响应内容: {response_json}")

        upload_url = response_json["data"]["uploadUrl"]
        file_id = response_json["data"]["fileId"]
        return f"{upload_url}?objectLength={file_size}", file_id

    def upload(self, upload_url: str, file_name: str, file_data: bytes) -> None:
        """
        上传

        :param upload_url:
        :param file_name:
        :param file_data:
        :return:
        """

        files = {
            "file": (file_name, file_data),
        }

        requests.request(
            method="POST",
            url=upload_url,
            files=files,
        )

    def upload_file(self, space_url: str, file_path: str) -> None:
        """
        上传单文件

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param file_path: 文件路径
        :return:
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]
        parent_id = space_info["parent_id"]

        file_name = os.path.basename(file_path)

        with open(file=file_path, mode="rb") as f:
            file_data = f.read()

        upload_url = self.perfect_files_pre_upload(
            owner_id=owner_id, parent_id=parent_id, file_name=file_name, file_size=len(file_data)
        )

        self.upload(upload_url=upload_url, file_name=file_name, file_data=file_data)

    def upload_folder(self, space_url: str, folder_path: str, space_info: dict = None) -> None:
        """
        上传文件夹

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param folder_path: 文件夹路径
        :param space_info: 空间信息（可选，避免重复查询）
        :return:
        """

        if space_info:
            owner_id = space_info["owner_id"]
            parent_id = space_info["parent_id"]
        else:
            space_info = self.get_space_info(space_url=space_url)
            owner_id = space_info["owner_id"]
            parent_id = space_info["parent_id"]

        for (dirpath, dirnames, filenames) in os.walk(top=folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)

                with open(file=file_path, mode="rb") as f:
                    file_data = f.read()

                upload_url = self.perfect_files_pre_upload(
                    owner_id=owner_id,
                    parent_id=parent_id,
                    file_name=os.path.relpath(path=file_path, start=os.path.join(folder_path, "..")),
                    file_size=len(file_data),
                )

                self.upload(upload_url=upload_url, file_name=filename, file_data=file_data)

    def perfect_files_get_forced_download_url(self, owner_id: int, file_id: int) -> str:
        """
        [API] 获取下载链接

        :param owner_id:
        :param file_id:
        :return:
        """
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/files/getForcedDownloadUrl/%d/%d" % (owner_id, file_id),
            headers=self.json_headers,
            cookies=self.cookies,
        )
        return response.json()["data"]["downloadUrl"]

    def download_file(self, file_url: str, folder_path: str) -> str:
        """
        下载单文件

        :param file_url: 文件链接
                    格式: https://onebox.huawei.com/v/<link_code>
        :param folder_path: 文件夹路径
        :return:
        """

        # 解析文件URL
        # 格式: https://onebox.huawei.com/v/<link_code>
        link_code = file_url.split("/")[-1]

        # 获取文件信息
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/v2/share/info/%s" % link_code,
            headers=self.json_headers,
            cookies=self.cookies,
        )
        file_info = response.json()["data"]

        owner_id = file_info["ownerId"]
        file_id = file_info["fileId"]
        file_name = file_info["fileName"]

        # 获取下载链接
        download_url = self.perfect_files_get_forced_download_url(owner_id=owner_id, file_id=file_id)

        # 下载文件
        response = requests.request(
            method="GET",
            url=download_url,
        )

        # 保存文件
        file_path = self._safe_join(folder_path, file_name)
        with open(file=file_path, mode="wb") as f:
            f.write(response.content)

        return file_path

    def download_folder_recursive(self, space_url: str, folder_path: str) -> None:
        """
        递归下载文件夹

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param folder_path: 文件夹路径
        :return:
        """

        file_list = self.list_folder_recursive(space_url=space_url)

        for file in file_list:
            if file["type"] == "file":
                # 下载文件
                file_url = "https://onebox.huawei.com/v/%s" % file["linkCode"]
                self.download_file(file_url=file_url, folder_path=folder_path)
            else:
                subfolder_path = self._safe_makedirs(folder_path, file["path"])

    def perfect_template_get_invitation_url(self, file_id: int, owner_id: int) -> str:
        """
        [API] 获取分享链接

        :param file_id:
        :param owner_id:
        :return:
        """

        payload = {
            "fileId": file_id,
            "ownerId": owner_id,
            "type": "0",
            "userId": "",
        }

        response = requests.request(
            method="POST",
            url="https://onebox.huawei.com/perfect/template/getInvitationUrl",
            headers=self.json_headers,
            json=payload,
            cookies=self.cookies,
        )
        invitation_url = response.json()["url"]

        return invitation_url

    def perfect_invite_edit_new_all_share(
            self, owner_id: int, file_id: int, link_code: str, link_role: LinkRole
    ) -> None:
        """
        [API] 设置分享权限，任意用户

        :param owner_id:
        :param file_id:
        :param link_code:
        :param link_role:
        :return:
        """

        payload = {
            "linkRole": link_role.value,
            "linkCode": link_code,
            "fileName": "",
            "accessCode": "",
            "effectiveAt": "",
            "expireAt": "",
            "urlAccess": "",
            "accessCodeMode": "",
        }

        payload_string = str(payload)
        payload_string = payload_string.replace("\'", "\"")
        payload_string = payload_string.replace(" ", "")
        invite_request_payload = {
            "inviteRequest": payload_string,
        }

        response = requests.request(
            method="POST",
            url="https://onebox.huawei.com/perfect/invite/edit/new/%d/%d" % (owner_id, file_id),
            headers=self.urlencoded_payload_headers,
            data=urllib.parse.urlencode(query=invite_request_payload),
            cookies=self.cookies,
        )

        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"设置分享权限失败，状态码: {response.status_code}, 响应内容: {response.text}")

        # 检查响应内容
        try:
            response_json = response.json()
            if response_json.get("code") != "success" and response_json.get("code") != "Success":
                print(f"[WARN] 设置分享权限可能失败，响应: {response_json}")
        except Exception as e:
            print(f"[WARN] 无法解析响应JSON: {e}, 响应内容: {response.text}")

    def perfect_invite_edit_new_specific_share(
            self, owner_id: int, file_id: int, link_code: str, link_role: LinkRole, login_name: str
    ) -> None:
        """
        [API] 设置分享权限，指定用户

        :param owner_id:
        :param file_id:
        :param link_code:
        :param link_role:
        :param login_name: w3 用户名
                    格式: a00123456
        :return:
        """

        payload = {
            "users": [{
                "cloudUserId": 0,
                "loginName": login_name,
                "role": link_role.value,
                "groupId": "",
                "aclId": "",
            }
            ],
            "linkRole": link_role.value,
            "linkCode": link_code,
            "fileName": "",
            "accessCode": "",
            "effectiveAt": "",
            "expireAt": "",
            "urlAccess": "",
            "accessCodeMode": "",
        }

        payload_string = str(payload)
        payload_string = payload_string.replace("\'", "\"")
        payload_string = payload_string.replace(" ", "")
        invite_request_payload = {
            "inviteRequest": payload_string,
        }

        response = requests.request(
            method="POST",
            url="https://onebox.huawei.com/perfect/invite/edit/new/%d/%d" % (owner_id, file_id),
            headers=self.urlencoded_payload_headers,
            data=urllib.parse.urlencode(query=invite_request_payload),
            cookies=self.cookies,
        )

        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"设置分享权限失败，状态码: {response.status_code}, 响应内容: {response.text}")

        # 检查响应内容
        try:
            response_json = response.json()
            if response_json.get("code") != "success" and response_json.get("code") != "Success":
                print(f"[WARN] 设置分享权限可能失败，响应: {response_json}")
        except Exception as e:
            print(f"[WARN] 无法解析响应JSON: {e}, 响应内容: {response.text}")

    def perfect_share_list(self, owner_id: int, parent_id: int, link_code: str) -> list:
        """
        [API] 单层列举分享文件夹

        :param owner_id:
        :param parent_id:
        :param link_code:
        :return:
        """
        PAGE_SIZE = 1000
        payload = {
            "ownerId": owner_id,
            "parentId": parent_id,
            "pageNumber": 1,
            "pageSize": PAGE_SIZE,
            "orderField": "name",
            "desc": "false",
            "token": "",
            "mode": "",
            "linkCode": link_code,
        }
        perfect_share_list_api = "https://onebox.huawei.com/perfect/share/list"
        response = requests.request(
            method="POST",
            url=perfect_share_list_api,
            headers=self.urlencoded_payload_headers,
            data=urllib.parse.urlencode(query=payload),
            cookies=self.cookies,
        )
        page_num = response.json()["data"]["totalPages"]
        file_list = []
        # noinspection PyTypeChecker
        for i in range(page_num):
            payload = {
                "ownerId": owner_id,
                "parentId": parent_id,
                "pageNumber": i + 1,
                "pageSize": PAGE_SIZE,
                "orderField": "name",
                "desc": "false",
                "token": "",
                "mode": "",
                "linkCode": link_code,
            }
            response = requests.request(
                method="POST",
                url=perfect_share_list_api,
                headers=self.urlencoded_payload_headers,
                data=urllib.parse.urlencode(query=payload),
                cookies=self.cookies,
            )
            file_list.extend(response.json()["data"]["content"])
        return file_list

    def list_share_folder(self, file_url: str) -> list:
        """
        单层遍历分享文件夹

        :param file_url: 文件链接
                    格式: https://onebox.huawei.com/v/<link_code>
        :return:
        """

        # 解析文件URL
        # 格式: https://onebox.huawei.com/v/<link_code>
        link_code = file_url.split("/")[-1]

        # 获取文件信息
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/v2/share/info/%s" % link_code,
            headers=self.json_headers,
            cookies=self.cookies,
        )
        file_info = response.json()["data"]

        owner_id = file_info["ownerId"]
        parent_id = file_info["fileId"]

        return self.perfect_share_list(owner_id=owner_id, parent_id=parent_id, link_code=link_code)

    def list_share_folder_recursive(self, file_url: str) -> list:
        """
        递归遍历分享文件夹

        :param file_url: 文件链接
                    格式: https://onebox.huawei.com/v/<link_code>
        :return:
        """

        # 解析文件URL
        # 格式: https://onebox.huawei.com/v/<link_code>
        link_code = file_url.split("/")[-1]

        # 获取文件信息
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/v2/share/info/%s" % link_code,
            headers=self.json_headers,
            cookies=self.cookies,
        )
        file_info = response.json()["data"]

        owner_id = file_info["ownerId"]

        # 广度优先搜索
        file_list = []
        queue = [{"parent_id": file_info["fileId"], "path": ""}]

        while len(queue) > 0:
            current = queue.pop(0)
            current_parent_id = current["parent_id"]
            current_path = current["path"]

            files = self.perfect_share_list(owner_id=owner_id, parent_id=current_parent_id, link_code=link_code)
            for file in files:
                file_path = os.path.join(current_path, file["name"])
                file["path"] = file_path
                file_list.append(file)

                if file["type"] == "folder":
                    queue.append({
                        "parent_id": file["id"],
                        "path": file_path
                    })

        return file_list

    def perfect_share_link_pre_upload(self, owner_id: int, parent_id: int, file_name: str, file_size: int, link_code: str) -> str:
        """
        [API] 预上传（分享链接）

        :param owner_id:
        :param parent_id:
        :param file_name:
        :param file_size:
        :param link_code:
        :return:
        """

        payload = {
            "ownerId": owner_id,
            "parentId": parent_id,
            "fileName": file_name,
            "fileSize": file_size,
            "linkCode": link_code,
        }

        perfect_share_link_pre_upload_api = "https://onebox.huawei.com/perfect/share/link/preUpload"
        response = requests.request(
            method="POST",
            url=perfect_share_link_pre_upload_api,
            headers=self.json_headers,
            json=payload,
            cookies=self.cookies,
        )
        upload_url = response.json()["data"]["uploadUrl"]
        return upload_url

    def upload_file_all_share(self, file_url: str, file_path: str) -> None:
        """
        上传文件，共享范围：任意用户

        :param file_url: 文件链接
                    格式: https://onebox.huawei.com/v/<link_code>
        :param file_path: 文件路径
        :return:
        """

        # 解析文件URL
        # 格式: https://onebox.huawei.com/v/<link_code>
        link_code = file_url.split("/")[-1]

        # 获取文件信息
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/v2/share/info/%s" % link_code,
            headers=self.json_headers,
            cookies=self.cookies,
        )
        file_info = response.json()["data"]

        owner_id = file_info["ownerId"]
        parent_id = file_info["fileId"]

        file_name = os.path.basename(file_path)

        with open(file=file_path, mode="rb") as f:
            file_data = f.read()

        upload_url = self.perfect_share_link_pre_upload(
            owner_id=owner_id, parent_id=parent_id, file_name=file_name, file_size=len(file_data), link_code=link_code
        )

        self.upload(upload_url=upload_url, file_name=file_name, file_data=file_data)

    def upload_folder_all_share(self, file_url: str, folder_path: str) -> None:
        """
        上传文件夹，共享范围：任意用户

        :param file_url: 文件链接
                    格式: https://onebox.huawei.com/v/<link_code>
        :param folder_path: 文件夹路径
        :return:
        """

        # 解析文件URL
        # 格式: https://onebox.huawei.com/v/<link_code>
        link_code = file_url.split("/")[-1]

        # 获取文件信息
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/v2/share/info/%s" % link_code,
            headers=self.json_headers,
            cookies=self.cookies,
        )
        file_info = response.json()["data"]

        owner_id = file_info["ownerId"]
        parent_id = file_info["fileId"]

        for (dirpath, dirnames, filenames) in os.walk(top=folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)

                with open(file=file_path, mode="rb") as f:
                    file_data = f.read()

                upload_url = self.perfect_share_link_pre_upload(
                    owner_id=owner_id,
                    parent_id=parent_id,
                    file_name=os.path.relpath(path=file_path, start=os.path.join(folder_path, "..")),
                    file_size=len(file_data),
                    link_code=link_code,
                )

                self.upload(upload_url=upload_url, file_name=filename, file_data=file_data)

    def upload_file_specific_share(self, file_url: str, file_path: str, login_name: str, link_role: LinkRole = LinkRole.viewer) -> None:
        """
        上传文件，共享范围：指定用户

        :param file_url: 文件链接
                    格式: https://onebox.huawei.com/v/<link_code>
        :param file_path: 文件路径
        :param login_name: w3 用户名，格式: a00123456
        :param link_role: 分享权限角色，默认为 viewer
        :return:
        """

        # 解析文件URL
        # 格式: https://onebox.huawei.com/v/<link_code>
        link_code = file_url.split("/")[-1]

        # 获取文件信息
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/v2/share/info/%s" % link_code,
            headers=self.json_headers,
            cookies=self.cookies,
        )
        file_info = response.json()["data"]

        owner_id = file_info["ownerId"]
        file_id = file_info["fileId"]

        file_name = os.path.basename(file_path)

        with open(file=file_path, mode="rb") as f:
            file_data = f.read()

        upload_url = self.perfect_share_link_pre_upload(
            owner_id=owner_id, parent_id=file_id, file_name=file_name, file_size=len(file_data), link_code=link_code
        )

        self.upload(upload_url=upload_url, file_name=file_name, file_data=file_data)

        # 设置分享权限，指定用户
        self.perfect_invite_edit_new_specific_share(
            owner_id=owner_id, file_id=file_id, link_code=link_code, link_role=link_role, login_name=login_name
        )

    def upload_folder_specific_share(self, file_url: str, folder_path: str, login_name: str, link_role: LinkRole = LinkRole.viewer) -> None:
        """
        上传文件夹，共享范围：指定用户

        :param file_url: 文件链接
                    格式: https://onebox.huawei.com/v/<link_code>
        :param folder_path: 文件夹路径
        :param login_name: w3 用户名，格式: a00123456
        :param link_role: 分享权限角色，默认为 viewer
        :return:
        """

        # 解析文件URL
        # 格式: https://onebox.huawei.com/v/<link_code>
        link_code = file_url.split("/")[-1]

        # 获取文件信息
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/v2/share/info/%s" % link_code,
            headers=self.json_headers,
            cookies=self.cookies,
        )
        file_info = response.json()["data"]

        owner_id = file_info["ownerId"]
        file_id = file_info["fileId"]

        for (dirpath, dirnames, filenames) in os.walk(top=folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)

                with open(file=file_path, mode="rb") as f:
                    file_data = f.read()

                upload_url = self.perfect_share_link_pre_upload(
                    owner_id=owner_id,
                    parent_id=file_id,
                    file_name=os.path.relpath(path=file_path, start=os.path.join(folder_path, "..")),
                    file_size=len(file_data),
                    link_code=link_code,
                )

                self.upload(upload_url=upload_url, file_name=filename, file_data=file_data)

        # 设置分享权限，指定用户
        self.perfect_invite_edit_new_specific_share(
            owner_id=owner_id, file_id=file_id, link_code=link_code, link_role=link_role, login_name=login_name
        )

    def perfect_share_get_forced_download_url(self, file_id: int, link_code: str) -> str:
        """
        [API] 获取下载链接（分享）

        :param file_id:
        :param link_code:
        :return:
        """
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/share/getForcedDownloadUrl/%d/%s" % (file_id, link_code),
            headers=self.json_headers,
            cookies=self.cookies,
        )
        return response.json()["data"]["downloadUrl"]

    def download_file_all_share(self, file_url: str, folder_path: str) -> str:
        """
        下载文件，共享范围：任意用户

        :param file_url: 文件链接
                    格式: https://onebox.huawei.com/v/<link_code>
        :param folder_path: 文件夹路径
        :return:
        """

        # 解析文件URL
        # 格式: https://onebox.huawei.com/v/<link_code>
        link_code = file_url.split("/")[-1]

        # 获取文件信息
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/v2/share/info/%s" % link_code,
            headers=self.json_headers,
            cookies=self.cookies,
        )
        file_info = response.json()["data"]

        owner_id = file_info["ownerId"]
        file_id = file_info["fileId"]
        file_name = file_info["fileName"]

        # 获取下载链接
        download_url = self.perfect_share_get_forced_download_url(file_id=file_id, link_code=link_code)

        # 下载文件
        response = requests.request(
            method="GET",
            url=download_url,
        )

        # 保存文件
        file_path = self._safe_join(folder_path, file_name)
        with open(file=file_path, mode="wb") as f:
            f.write(response.content)

        return file_path

    def download_folder_recursive_all_share(self, file_url: str, folder_path: str) -> None:
        """
        递归下载文件夹，共享范围：任意用户

        :param file_url: 文件链接
                    格式: https://onebox.huawei.com/v/<link_code>
        :param folder_path: 文件夹路径
        :return:
        """

        file_list = self.list_share_folder_recursive(file_url=file_url)

        for file in file_list:
            if file["type"] == "file":
                # 下载文件
                download_url = self.perfect_share_get_forced_download_url(file_id=file["id"], link_code=file["linkCode"])
                response = requests.request(
                    method="GET",
                    url=download_url,
                )

                # 保存文件
                file_path = self._safe_join(folder_path, file["path"])
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file=file_path, mode="wb") as f:
                    f.write(response.content)
            else:
                self._safe_makedirs(folder_path, file["path"])

    def download_file_specific_share(self, file_url: str, folder_path: str) -> str:
        """
        下载文件，共享范围：指定用户

        :param file_url: 文件链接
                    格式: https://onebox.huawei.com/v/<link_code>
        :param folder_path: 文件夹路径
        :return:
        """

        # 解析文件URL
        # 格式: https://onebox.huawei.com/v/<link_code>
        link_code = file_url.split("/")[-1]

        # 获取文件信息
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/v2/share/info/%s" % link_code,
            headers=self.json_headers,
            cookies=self.cookies,
        )
        file_info = response.json()["data"]

        owner_id = file_info["ownerId"]
        file_id = file_info["fileId"]
        file_name = file_info["fileName"]

        # 获取下载链接
        download_url = self.perfect_share_get_forced_download_url(file_id=file_id, link_code=link_code)

        # 下载文件
        response = requests.request(
            method="GET",
            url=download_url,
        )

        # 保存文件
        file_path = self._safe_join(folder_path, file_name)
        with open(file=file_path, mode="wb") as f:
            f.write(response.content)

        return file_path

    def download_folder_recursive_specific_share(self, file_url: str, folder_path: str) -> None:
        """
        递归下载文件夹，共享范围：指定用户

        :param file_url: 文件链接
                    格式: https://onebox.huawei.com/v/<link_code>
        :param folder_path: 文件夹路径
        :return:
        """

        file_list = self.list_share_folder_recursive(file_url=file_url)

        for file in file_list:
            if file["type"] == "file":
                # 下载文件
                download_url = self.perfect_share_get_forced_download_url(file_id=file["id"], link_code=file["linkCode"])
                response = requests.request(
                    method="GET",
                    url=download_url,
                )

                # 保存文件
                file_path = self._safe_join(folder_path, file["path"])
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file=file_path, mode="wb") as f:
                    f.write(response.content)
            else:
                self._safe_makedirs(folder_path, file["path"])

    def get_file_info(self, file_url: str) -> dict:
        """
        获取文件信息

        :param file_url: 文件链接
                    格式: https://onebox.huawei.com/v/<link_code>
        :return:
        """

        # 解析文件URL
        # 格式: https://onebox.huawei.com/v/<link_code>
        link_code = file_url.split("/")[-1]

        # 获取文件信息
        response = requests.request(
            method="GET",
            url="https://onebox.huawei.com/perfect/v2/share/info/%s" % link_code,
            headers=self.json_headers,
            cookies=self.cookies,
        )
        file_info = response.json()["data"]

        return file_info

    def copy_file(self, space_url: str, file_id: int, target_parent_id: int) -> None:
        """
        复制文件

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param file_id: 文件ID
        :param target_parent_id: 目标父文件夹ID
        :return:
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]

        payload = {
            "ownerId": owner_id,
            "targetParentId": target_parent_id,
            "nodes": [
                {
                    "id": file_id,
                    "type": "file",
                }
            ],
        }

        perfect_nodes_copy_api = "https://onebox.huawei.com/perfect/nodes/copy"
        requests.request(
            method="POST",
            url=perfect_nodes_copy_api,
            headers=self.json_headers,
            json=payload,
            cookies=self.cookies,
        )

    def copy_folder(self, space_url: str, folder_id: int, target_parent_id: int) -> None:
        """
        复制文件夹

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param folder_id: 文件夹ID
        :param target_parent_id: 目标父文件夹ID
        :return:
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]

        payload = {
            "ownerId": owner_id,
            "targetParentId": target_parent_id,
            "nodes": [
                {
                    "id": folder_id,
                    "type": "folder",
                }
            ],
        }

        perfect_nodes_copy_api = "https://onebox.huawei.com/perfect/nodes/copy"
        requests.request(
            method="POST",
            url=perfect_nodes_copy_api,
            headers=self.json_headers,
            json=payload,
            cookies=self.cookies,
        )

    def perfect_nodes_delete(self, owner_id: int, node_id: int, node_type: str) -> None:
        """
        [API] 删除节点（文件或文件夹）

        :param owner_id:
        :param node_id:
        :param node_type: "file" 或 "folder"
        :return:
        """

        payload = {
            "ownerId": owner_id,
            "nodes": [
                {
                    "id": node_id,
                    "type": node_type,
                }
            ],
        }

        perfect_nodes_delete_api = "https://onebox.huawei.com/perfect/nodes/delete"
        requests.request(
            method="POST",
            url=perfect_nodes_delete_api,
            headers=self.json_headers,
            json=payload,
            cookies=self.cookies,
        )

    def delete_file_to_recycle_bin(self, space_url: str, file_id: int) -> None:
        """
        删除文件到回收站

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param file_id: 文件ID
        :return:
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]

        self.perfect_nodes_delete(owner_id=owner_id, node_id=file_id, node_type="file")

    def delete_folder_to_recycle_bin(self, space_url: str, folder_id: int) -> None:
        """
        删除文件夹到回收站

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param folder_id: 文件夹ID
        :return:
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]

        self.perfect_nodes_delete(owner_id=owner_id, node_id=folder_id, node_type="folder")

    def perfect_nodes_rename(self, owner_id: int, node_id: int, node_type: str, new_name: str) -> None:
        """
        [API] 重命名节点（文件或文件夹）

        :param owner_id:
        :param node_id:
        :param node_type: "file" 或 "folder"
        :param new_name: 新名称
        :return:
        """

        payload = {
            "ownerId": owner_id,
            "nodes": [
                {
                    "id": node_id,
                    "type": node_type,
                    "newName": new_name,
                }
            ],
        }

        perfect_nodes_rename_api = "https://onebox.huawei.com/perfect/nodes/rename"
        requests.request(
            method="POST",
            url=perfect_nodes_rename_api,
            headers=self.json_headers,
            json=payload,
            cookies=self.cookies,
        )

    def rename_file(self, space_url: str, file_id: int, new_name: str) -> None:
        """
        重命名文件

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param file_id: 文件ID
        :param new_name: 新名称
        :return:
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]

        self.perfect_nodes_rename(owner_id=owner_id, node_id=file_id, node_type="file", new_name=new_name)

    def rename_folder(self, space_url: str, folder_id: int, new_name: str) -> None:
        """
        重命名文件夹

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param folder_id: 文件夹ID
        :param new_name: 新名称
        :return:
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]

        self.perfect_nodes_rename(owner_id=owner_id, node_id=folder_id, node_type="folder", new_name=new_name)

    def perfect_trash_delete(self, owner_id: int, node_id: int, node_type: str) -> None:
        """
        [API] 彻底删除节点（文件或文件夹）- 从回收站删除

        :param owner_id:
        :param node_id:
        :param node_type: "file" 或 "folder"
        :return:
        """

        payload = {
            "ownerId": owner_id,
            "nodes": [
                {
                    "id": node_id,
                    "type": node_type,
                }
            ],
        }

        perfect_trash_delete_api = "https://onebox.huawei.com/perfect/trash/delete"
        requests.request(
            method="POST",
            url=perfect_trash_delete_api,
            headers=self.json_headers,
            json=payload,
            cookies=self.cookies,
        )

    def delete_file_completely(self, space_url: str, file_id: int) -> None:
        """
        彻底删除文件（从回收站删除）

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param file_id: 文件ID
        :return:
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]

        self.perfect_trash_delete(owner_id=owner_id, node_id=file_id, node_type="file")

    def delete_folder_completely(self, space_url: str, folder_id: int) -> None:
        """
        彻底删除文件夹（从回收站删除）

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param folder_id: 文件夹ID
        :return:
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]

        self.perfect_trash_delete(owner_id=owner_id, node_id=folder_id, node_type="folder")

    def perfect_trash_restore(self, owner_id: int, node_id: int, node_type: str, target_parent_id: int) -> None:
        """
        [API] 恢复节点（文件或文件夹）- 从回收站恢复

        :param owner_id:
        :param node_id:
        :param node_type: "file" 或 "folder"
        :param target_parent_id: 目标父文件夹ID
        :return:
        """

        payload = {
            "ownerId": owner_id,
            "nodes": [
                {
                    "id": node_id,
                    "type": node_type,
                    "targetParentId": target_parent_id,
                }
            ],
        }

        perfect_trash_restore_api = "https://onebox.huawei.com/perfect/trash/restore"
        requests.request(
            method="POST",
            url=perfect_trash_restore_api,
            headers=self.json_headers,
            json=payload,
            cookies=self.cookies,
        )

    def restore_file(self, space_url: str, file_id: int, target_parent_id: int) -> None:
        """
        恢复文件（从回收站恢复）

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param file_id: 文件ID
        :param target_parent_id: 目标父文件夹ID
        :return:
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]

        self.perfect_trash_restore(owner_id=owner_id, node_id=file_id, node_type="file", target_parent_id=target_parent_id)

    def restore_folder(self, space_url: str, folder_id: int, target_parent_id: int) -> None:
        """
        恢复文件夹（从回收站恢复）

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param folder_id: 文件夹ID
        :param target_parent_id: 目标父文件夹ID
        :return:
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]

        self.perfect_trash_restore(owner_id=owner_id, node_id=folder_id, node_type="folder", target_parent_id=target_parent_id)

    def perfect_trash_clean(self) -> None:
        """
        [API] 清空回收站

        :return:
        """

        perfect_trash_clean_api = "https://onebox.huawei.com/perfect/trash/clean"
        requests.request(
            method="POST",
            url=perfect_trash_clean_api,
            headers=self.json_headers,
            cookies=self.cookies,
        )

    def perfect_trash_restore_all(self) -> None:
        """
        [API] 恢复回收站所有文件

        :return:
        """

        perfect_trash_restore_all_api = "https://onebox.huawei.com/perfect/trash/restoreAll"
        requests.request(
            method="POST",
            url=perfect_trash_restore_all_api,
            headers=self.json_headers,
            cookies=self.cookies,
        )

    def create_folder(self, space_url: str, folder_name: str) -> int:
        """
        创建文件夹

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param folder_name: 文件夹名称
        :return: 文件夹ID
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]
        parent_id = space_info["parent_id"]

        payload = {
            "ownerId": owner_id,
            "parentId": parent_id,
            "name": folder_name,
        }

        perfect_folders_create_api = "https://onebox.huawei.com/perfect/folders/create"
        response = requests.request(
            method="POST",
            url=perfect_folders_create_api,
            headers=self.json_headers,
            json=payload,
            cookies=self.cookies,
        )

        response_json = response.json()
        print(f"[DEBUG] create_folder response: {response_json}")
        
        # 尝试获取folder_id
        if "data" in response_json and "id" in response_json["data"]:
            folder_id = response_json["data"]["id"]
        elif "id" in response_json:
            folder_id = response_json["id"]
        else:
            print(f"[ERROR] create_folder响应格式异常: {response_json}")
            raise ValueError(f"无法从响应中获取文件夹ID: {response_json}")
            
        return folder_id

    def create_blank_document(self, space_url: str, file_name: str, document_type: str) -> int:
        """
        创建空白文档

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param file_name: 文件名称
        :param document_type: 文档类型
                    格式: "word", "excel", "ppt", "mind", "form", "online_doc"
        :return: 文件ID
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]
        parent_id = space_info["parent_id"]

        payload = {
            "ownerId": owner_id,
            "parentId": parent_id,
            "name": file_name,
            "docType": document_type,
        }

        perfect_files_create_api = "https://onebox.huawei.com/perfect/files/create"
        response = requests.request(
            method="POST",
            url=perfect_files_create_api,
            headers=self.json_headers,
            json=payload,
            cookies=self.cookies,
        )

        file_id = response.json()["data"]["id"]
        return file_id

    def create_document(self, space_url: str, file_name: str, template_id: int) -> int:
        """
        创建文档（使用模板）

        :param space_url: 空间链接
                    格式: https://onebox.huawei.com/<space_type>/1/<parent_id>/<owner_id>
        :param file_name: 文件名称
        :param template_id: 模板ID
        :return: 文件ID
        """

        space_info = self.get_space_info(space_url=space_url)
        owner_id = space_info["owner_id"]
        parent_id = space_info["parent_id"]

        payload = {
            "ownerId": owner_id,
            "parentId": parent_id,
            "name": file_name,
            "templateId": template_id,
        }

        perfect_files_create_api = "https://onebox.huawei.com/perfect/files/create"
        response = requests.request(
            method="POST",
            url=perfect_files_create_api,
            headers=self.json_headers,
            json=payload,
            cookies=self.cookies,
        )

        file_id = response.json()["data"]["id"]
        return file_id
