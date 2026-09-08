# Python 检视规则

## 安全合规

### PY-SEC-001: 禁止字符串拼接构造SQL语句
- **检查锚点**: %格式化SQL, f-string构造SQL, +拼接SQL字符串, execute(拼接字符串)
- **反例**: cursor.execute("SELECT * FROM user WHERE id=" + user_id)
- **正例**: cursor.execute("SELECT * FROM user WHERE id=%s", (user_id,))

### PY-SEC-002: 禁止使用shell=True执行系统命令
- **检查锚点**: subprocess.call(shell=True), subprocess.run(shell=True), os.system(
- **反例**: subprocess.run("ls " + user_input, shell=True)
- **正例**: subprocess.run(["ls", user_input])

### PY-SEC-003: 禁止硬编码凭据和密钥
- **检查锚点**: password=, secret=, api_key=, token=, 硬编码的字符串值包含敏感关键词
- **反例**: DB_PASSWORD = "admin123"
- **正例**: DB_PASSWORD = os.environ["DB_PASSWORD"]

### PY-SEC-004: 禁止使用不安全的反序列化
- **检查锚点**: pickle.load, pickle.loads, yaml.load(unsafe Loader), yaml.unsafe_load
- **反例**: data = pickle.loads(external_data)
- **正例**: data = json.loads(external_data)

### PY-SEC-005: 禁止禁用SSL/TLS证书验证
- **检查锚点**: verify=False, ssl._create_unverified_context, CERT_NONE
- **反例**: requests.get(url, verify=False)
- **正例**: requests.get(url, verify=True)

### PY-SEC-006: 禁止在日志中输出敏感数据
- **检查锚点**: logger.debug(password), log.info(token), print(敏感变量)
- **反例**: logger.info(f"User password: {password}")

### PY-SEC-007: 禁止使用非安全方式创建临时文件
- **检查锚点**: tempfile.mktemp, tempfile.mkdtemp, tempfile.NamedTemporaryFile
- **反例**: `filename = tempfile.mktemp()`
- **正例**: `filename = tempfile.mkstemp()`

### PY-SEC-008: 禁止通过异常泄露敏感数据
- **检查锚点**: raise Error(username, password)
- **反例**: `raise UnauthorizedError('user %s or password %s is wrong' % (username, password))`

## 并发安全

### PY-CON-001: 禁止无锁访问共享可变状态
- **检查锚点**: 全局list/dict在多线程中读写, 非线程安全集合在多线程中使用
- **反例**: shared_dict[key] = value  # 多线程无锁
- **正例**: with lock: shared_dict[key] = value

### PY-CON-002: 禁止在async函数中调用阻塞IO
- **检查锚点**: time.sleep在async函数中, requests.get在async函数中, 同步IO在async中
- **反例**: async def handler(): time.sleep(5)
- **正例**: async def handler(): await asyncio.sleep(5)

### PY-CON-003: 必须处理async任务取消和超时
- **检查锚点**: asyncio.wait_for, asyncio.shield, CancelledError未捕获
- **正例**: try: await asyncio.wait_for(coro, timeout=30) except asyncio.TimeoutError: ...

## 编码规范

### PY-CODE-001: 禁止使用可变对象作为函数默认参数
- **检查锚点**: def func(arg=list()), def func(arg=dict()), def func(arg=[])
- **反例**: def append(item, lst=[]): lst.append(item)
- **正例**: def append(item, lst=None): lst = lst or []; lst.append(item)

### PY-CODE-002: 禁止空except吞没异常
- **检查锚点**: except:, except Exception: pass, except Exception: 后无操作
- **反例**: try: ... except: pass
- **正例**: try: ... except ValueError as e: logger.error(e)

### PY-CODE-003: 禁止使用通配符导入
- **检查锚点**: from module import *, from xxx import *
- **反例**: from os import *
- **正例**: import os

### PY-CODE-004: 禁止遮蔽内置名称
- **检查锚点**: 变量名为list, dict, str, int, sum, id, type, input, min, max
- **反例**: list = [1, 2, 3]
- **正例**: item_list = [1, 2, 3]

### PY-CODE-005: 必须使用上下文管理器操作资源
- **检查锚点**: open()未使用with, 连接未使用with, 锁未使用with
- **反例**: f = open("file.txt"); data = f.read(); f.close()
- **正例**: with open("file.txt") as f: data = f.read()

### PY-CODE-006: 禁止保留调试打印和注释掉的代码
- **检查锚点**: print(, breakpoint(), 注释掉的代码块

### PY-CODE-007: 必须使用functools.wraps装饰装饰器函数
- **检查锚点**: def wrapper(*args, **kwargs): 未加@functools.wraps

### PY-CODE-008: 禁止使用裸类型Any替代具体类型标注
- **检查锚点**: -> Any, : Any, var: Any =, 函数签名全为Any
- **反例**: def process(data: Any) -> Any:
- **正例**: def process(data: list[str]) -> dict[str, int]:

### PY-CODE-009: 禁止未验证的用户输入直接用于文件路径
- **检查锚点**: os.path.join(user_input), open(user_input), 用户输入拼接到路径

## 性能优化

### PY-PERF-001: 禁止在循环中使用+拼接字符串
- **检查锚点**: result += item在for循环中, 字符串+拼接在循环体内
- **反例**: result = ""; for s in strings: result += s
- **正例**: result = "".join(strings)

### PY-PERF-002: 禁止在循环中执行数据库查询（N+1问题）
- **检查锚点**: Model.objects.get/filter在for循环内, 查询方法在循环体内
- **反例**: for id in ids: obj = Model.objects.get(pk=id)
- **正例**: objs = Model.objects.filter(pk__in=ids)

### PY-PERF-003: 禁止对列表头部执行insert或pop(0)
- **检查锚点**: list.insert(0, ...), list.pop(0)
- **反例**: items.insert(0, new_item)
- **正例**: from collections import deque; items = deque(); items.appendleft(new_item)

### PY-PERF-004: 必须对频繁调用的正则表达式预编译
- **检查锚点**: re.match/re.search/re.sub在循环或高频函数内
- **反例**: for line in lines: m = re.search(pattern, line)
- **正例**: compiled = re.compile(pattern); for line in lines: m = compiled.search(line)

### PY-PERF-005: 必须使用生成器处理大规模数据
- **检查锚点**: list comprehension用于大数据集, 一次性load全量数据到内存
- **反例**: data = [process(x) for x in large_dataset]
- **正例**: data = (process(x) for x in large_dataset)

## 架构设计

### PY-ARCH-001: 禁止循环导入
- **检查锚点**: 模块A导入B且B导入A, ImportError at runtime

### PY-ARCH-002: 必须使用类型标注声明公共API
- **检查锚点**: def函数无类型标注, class方法缺少返回类型
- **正例**: def get_user(user_id: int) -> User:

### PY-ARCH-003: 禁止硬编码配置值
- **检查锚点**: 代码中直接写入IP/端口/路径等配置字面值

### PY-ARCH-004: 禁止过度嵌套（超过3层）
- **检查锚点**: if嵌套超过3层, for嵌套超过3层, try嵌套超过3层

### PY-ARCH-005: 禁止函数超过50行或参数超过5个
- **检查锚点**: def函数体过长, 函数参数列表过长