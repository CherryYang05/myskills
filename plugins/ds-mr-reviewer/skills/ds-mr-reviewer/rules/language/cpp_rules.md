# C++ 检视规则

## 内存管理

### C_CPP-MEM-001: malloc/calloc申请内存后必须判空
- **检查锚点**: malloc(, calloc(, realloc(, 返回值未与NULL比较
- **反例**: `char *buf = malloc(size); buf[0] = 'a';`
- **正例**: `char *buf = malloc(size); if (buf == NULL) { return ERROR; }`

### C_CPP-MEM-002: 检查内存配对使用、防止资源泄漏和重复释放
- **检查锚点**: malloc/free配对, new/delete配对, new[]/delete[]配对, open/close配对, fopen/fclose配对
- **反例**: `char *buf = malloc(size); return; // 未free`
- **正例**: `char *buf = malloc(size); ... free(buf); buf = NULL;`

### C_CPP-MEM-003: 结构体、数组、指针使用前必须初始化
- **检查锚点**: struct声明后未memset, 数组声明未初始化, 指针声明未赋值
- **正例**: `memset(&info, 0, sizeof(info));`

### C_CPP-MEM-004: cJSON库内存释放必须使用正确的配对函数
- **检查锚点**: cJSON_Parse/cJSON_Delete配对, cJSON_Print/cJSON_Free配对
- **反例**: `cJSON *root = cJSON_Parse(str); ... return; // 未cJSON_Delete`
- **正例**: `cJSON *root = cJSON_Parse(str); ... cJSON_Delete(root);`

## 指针操作

### C_CPP-MEM-005: 非static接口的指针入参必须判空，二级指针入参必须判空
- **检查锚点**: 函数参数为指针类型, 函数体未检查NULL, 二级指针入参未判空, 数字入参按需校验合法范围
- **反例**: `void process(char *data) { int len = strlen(data); }`
- **正例**: `void process(char *data) { if (data == NULL) { return; } }`

### C_CPP-MEM-006: 禁止整数与指针互相转化，禁止对指针进行逻辑或位运算
- **检查锚点**: (int)ptr, (void *)int_value, 指针参与|, &, ^运算
- **反例**: `int addr = (int)ptr;`

### C_CPP-MEM-007: 必须检查第三方库函数返回值
- **检查锚点**: cJSON_Parse返回值未判空, cJSON_Print返回值未判空

### C_CPP-MEM-008: AtpMsg消息转换成指针前，需要使用dataLen成员判断长度
- **检查锚点**: AtpMsg转指针, dataLen未检查, 消息体长度校验

## 整数运算

### C_CPP-MEM-009: 检查算术运算中的整数溢出和除零错误
- **检查锚点**: 乘法运算结果可能溢出, 除法运算除数可能为零
- **反例**: `int result = a * b;`
- **正例**: `if (a > INT_MAX / b) { return ERROR; } int result = a * b;`

### C_CPP-MEM-010: 禁止对有符号数做位运算
- **检查锚点**: signed int/long参与<<, >>, &, |, ^运算

### C_CPP-MEM-011: 检查有符号/无符号比较问题
- **检查锚点**: signed与unsigned变量比较, size_t与int比较, 循环变量类型不匹配
- **反例**: `if (len < 0 || len >= max_size) // len为size_t，永远>=0`

## 循环控制

### C_CPP-CODE-001: 检查循环次数受外部数据控制时的合法性校验
- **检查锚点**: for/while循环条件来自外部输入, 循环次数无上限保护

### C_CPP-CODE-002: 禁止使用浮点数作为循环计数器
- **检查锚点**: float/double用作for循环变量, while条件使用浮点比较
- **反例**: `for (float i = 0.0; i < 1.0; i += 0.1) { ... }`
- **正例**: `for (int i = 0; i < 10; i++) { ... }`

## 系统资源

### C_CPP-CODE-003: 文件打开/关闭必须配对，返回值必须检查
- **检查锚点**: fopen/open返回值未检查, 文件路径未校验, 临时文件创建不安全

### C_CPP-CODE-004: 确保系统资源的正确获取和释放
- **检查锚点**: 资源获取与释放不在同一层次, 异常路径下资源未释放

## 敏感信息

### C_CPP-CODE-005: 禁止打印敏感信息
- **检查锚点**: printf/LOG输出包含key,token,rand,mac,sn,ip等敏感字段

### C_CPP-CODE-006: 敏感信息使用完成后必须显式清零
- **检查锚点**: 敏感数据存放在栈/堆变量中, 函数返回前未memset清零
- **反例**: `char password[64]; ... return;`
- **正例**: `char password[64]; ... memset(password, 0, sizeof(password));`

### C_CPP-CODE-007: 禁止硬编码敏感信息，必须加密保存
- **检查锚点**: 代码中直接写入密码,密钥,token等字面值

## 格式化

### C_CPP-CODE-008: 日志打印%s前必须排查是否会打印空指针
- **检查锚点**: printf/sprintf/snprintf的%s参数, 参数可能为NULL

### C_CPP-CODE-009: 禁止format参数外部输入，防止注入漏洞
- **检查锚点**: printf(user_input), syslog(user_input), 格式化字符串来自外部
- **反例**: `printf(external_msg);`
- **正例**: `printf("%s", external_msg);`

### C_CPP-CODE-010: 确保format中参数类型与个数与实际参数一致
- **检查锚点**: printf格式串与参数不匹配, %d对应long, %s对应非字符串

### C_CPP-CODE-011: 必须使用安全函数并检查返回值
- **检查锚点**: memcpy_s, strcpy_s, strncpy_s, sprintf_s, 禁止使用memcpy/strcpy/sprintf等不安全函数
- **反例**: `strcpy(dest, src);`
- **正例**: `if (strcpy_s(dest, destMax, src) != EOK) { return ERROR; }`

## 接口定义

### C_CPP-CODE-012: 非static函数必须对入参进行合法性检查
- **检查锚点**: 对外暴露的函数, 指针入参未判空, 外部输入数据未校验

### C_CPP-CODE-013: 禁止直接使用外部输入作为数组下标、内存分配长度、循环条件
- **检查锚点**: 外部输入直接用作数组下标, malloc参数, 循环上限
- **反例**: `char *buf = malloc(external_size);`
- **正例**: `if (external_size > MAX_SIZE) { return ERROR; } char *buf = malloc(external_size);`

## 逻辑问题

### C_CPP-CODE-014: 检查恒为真/假的条件判断
- **检查锚点**: if(true), if(false), 永真/永假条件, 条件判断逻辑错误

### C_CPP-CODE-015: 识别并删除不会进入的分支
- **检查锚点**: return后的代码, if-else中不可达分支, 死代码

## 多线程

### C_CPP-CON-001: 共享数据必须保证线程安全
- **检查锚点**: 全局变量/静态变量在多线程中读写, 共享资源无锁保护
- **反例**: `static int counter; // 多线程中counter++`
- **正例**: `static std::atomic<int> counter;`

### C_CPP-CON-002: 正确使用互斥锁并防止死锁
- **检查锚点**: lock/unlock配对, 多个锁的获取顺序不一致, 锁获取后异常路径未释放
- **正例**: `std::lock_guard<std::mutex> guard(mtx);`

### C_CPP-CON-003: spinlock锁内禁止打印日志
- **检查锚点**: spinlock, spin_lock, spin_trylock, LOG_DEBUG, LOG_INFO, printf, printk
- **反例**: `spin_lock(&lock); LOG_DEBUG("processing..."); spin_unlock(&lock);`
- **正例**: `spin_lock(&lock); Process(); spin_unlock(&lock); // 锁内无日志打印`

### C_CPP-CON-004: spinlock锁内禁止切换线程
- **检查锚点**: spinlock, sched_yield, sleep, usleep, msleep, thread yield, 线程切换
- **反例**: `spin_lock(&lock); sleep(1); spin_unlock(&lock); // 锁内休眠会导致死锁`
- **正例**: `spin_lock(&lock); ProcessNoBlocking(); spin_unlock(&lock);`

### C_CPP-CON-005: spinlock锁内禁止执行长时间操作
- **检查锚点**: spinlock, 长时间操作, IO操作, 磁盘IO, 网络IO, 等待锁
- **反例**: `spin_lock(&lock); ReadFileFromDisk(); spin_unlock(&lock); // 锁内IO会长期占锁`
- **正例**: `spin_unlock(&lock); ReadFileFromDisk(); spin_lock(&lock); // 锁外执行IO`

### C_CPP-MEM-012: 调用异步接口后禁止再访问可能已被释放的资源对象
- **检查锚点**: 异步接口, async_call, 资源释放后访问, use-after-free, 悬空指针
- **反例**: `AsyncFree(ptr); pData->value = 1; // 异步释放后继续访问`
- **正例**: `AsyncFree(ptr); ptr = NULL; // 立即置空防止后续访问`

### C_CPP-MEM-013: 调用回调函数的callback后禁止再访问可能已被释放的资源
- **检查锚点**: callback执行后, 回调函数, callback后访问, 资源释放
- **反例**: `callback(data); FreeData(data); data->value = 1; // callback可能已释放data`
- **正例**: `callback(data); // 不再访问data，或在callback内部完成所有操作`

## 日志

### C_CPP-LOG-001: 日志内容必须使用英文记录
- **检查锚点**: 中文注释, 中文拼音, 中文标点符号, unicode中文字符
- **反例**: `LOG_INFO("开始处理请求"); LOG_DEBUG("请求成功啦");`
- **正例**: `LOG_INFO("Start processing request"); LOG_DEBUG("Request processed successfully");`

### C_CPP-LOG-002: 日志描述语句必须采用陈述句格式，使用过去时或进行时
- **检查锚点**: Succeeded, Failed, Starting, Processing, Completed, 正在处理, 已完成
- **反例**: `LOG_INFO("Will process request"); LOG_DEBUG("Processing is running");`
- **正例**: `LOG_INFO("Processing request"); LOG_DEBUG("Succeeded to process request");`

### C_CPP-LOG-003: 禁止在循环体内打印正常的INFO级别日志
- **检查锚点**: for循环, while循环, do-while, 循环体内LOG_INFO, 循环内打印正常日志
- **反例**: `for (int i = 0; i < 1000; i++) { LOG_INFO("processing item %d", i); }`
- **正例**: `for (int i = 0; i < 1000; i++) { ProcessItem(i); } LOG_INFO("Processed %d items", count);`

### C_CPP-LOG-004: 禁止在日志中以明文形式记录敏感信息
- **检查锚点**: password, 密码, 密钥, key, token, credit card, 敏感信息明文
- **反例**: `LOG_INFO("User login: name=%s, password=%s", name, pwd); // 密码明文打印`
- **正例**: `LOG_INFO("User login: name=%s, password=***", name, pwd); // 脱敏处理`

## 编码规范

### C_CPP-CODE-016: 内部函数必须使用static修饰
- **检查锚点**: 非static函数仅在本文件内被调用, 函数声明缺少static

### C_CPP-CODE-017: 检查安全函数使用、destMax参数设置、禁止封装安全函数
- **检查锚点**: 安全函数destMax参数设置不当, 封装安全函数丢失安全检查

### C_CPP-CODE-018: 必须检查系统调用与标准库函数的返回值
- **检查锚点**: snprintf, sprintf, save_, write, fread, 涉及文件/配置保存的操作
- **反例**: `snprintf(buf, size, "%s", str); // 未检查是否截断或失败`
- **正例**: `if (snprintf(buf, size, "%s", str) < 0) { return ERROR; }`

## 模块设计

### C_CPP-ARCH-001: 模块必须遵循单一职责原则
- **检查锚点**: 单个模块职责过多, 模块对外暴露过多接口, 模块间耦合过紧
