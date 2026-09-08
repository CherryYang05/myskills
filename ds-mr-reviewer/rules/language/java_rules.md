# Java 检视规则

## 安全合规

### JAVA-SEC-001: 禁止SQL注入
- **检查锚点**: Statement.executeQuery(拼接字符串), Statement.executeUpdate(拼接), JDBC拼SQL
- **反例**: "SELECT * FROM user WHERE id=" + userId
- **正例**: PreparedStatement ps = conn.prepareStatement("SELECT * FROM user WHERE id=?");

### JAVA-SEC-002: 禁止XSS跨站脚本攻击
- **检查锚点**: 直接输出用户输入, response.getWriter().write用户输入, HTML未编码
- **反例**: out.println(userInput)
- **正例**: 使用HTML编码后再输出

### JAVA-SEC-003: 禁止命令注入
- **检查锚点**: Runtime.exec(), ProcessBuilder, Runtime.getRuntime().exec拼字符串
- **反例**: Runtime.getRuntime().exec("ls " + userInput)
- **正例**: 使用数组形式传递命令参数

### JAVA-SEC-004: 禁止不安全的反序列化
- **检查锚点**: ObjectInputStream, readObject, XMLDecoder, YAML库unsafe load
- **反例**: objInput.readObject()
- **正例**: 使用白名单或JSON等安全替代方案

### JAVA-SEC-005: 禁止硬编码密码和密钥
- **检查锚点**: password=, pwd=, secret=, token=, apiKey=, 硬编码字符串值包含敏感关键词
- **反例**: String password = "admin123";
- **正例**: String password = System.getenv("DB_PASSWORD");

### JAVA-SEC-006: 禁止不安全的加密使用
- **检查锚点**: DES, MD5, SHA1用于加密, 硬编码密钥, 不安全的加密算法
- **正例**: 使用AES, SHA-256及以上, 密钥从安全的密钥存储获取

### JAVA-SEC-007: 禁止敏感信息泄露
- **检查锚点**: logger.debug敏感信息, 异常堆栈打印, System.out.print密码
- **反例**: logger.debug("Password: " + password)
- **正例**: 日志中脱敏处理

### JAVA-SEC-008: 禁止文件路径注入
- **检查锚点**: FileInputStream用户输入, Paths.get用户输入, 文件路径拼接用户输入
- **反例**: new FileInputStream(userInput)
- **正例**: 验证文件路径在允许目录内

### JAVA-SEC-009: 禁止LDAP注入
- **检查锚点**: DirContext.search拼用户输入, LDAP查询拼接用户输入
- **反例**: search("uid=" + userInput + ",dc=example,dc=com")
- **正例**: 使用参数化查询

## 并发安全

### JAVA-CON-001: 禁止在可并发线程安全的类中使用非线程安全的数据结构（数据结构操作安全）
- **检查锚点**: static可变集合(HashMap,ArrayList等)在多线程中读写, 非volatile/Atomic的static变量
- **反例**: private static Map<String, Object> cache = new HashMap<>();
- **正例**: private static final ConcurrentHashMap<String, Object> cache = new ConcurrentHashMap<>();

### JAVA-CON-002: 禁止在支持并发的类中，及时使用线程安全的数据结构，也不能带有状态的类属性（业务安全）

- **检查锚点**: 类属性的新增，在单例或者工具类 等支持线程安全的类中，使用时间戳，计数器【非静态常量】等等带有状态的属性，即便属性本身是线程安全的比如使用了Automic或者Concurrent等数据结构，并不能保证参与上下文过程计算中是线程安全的，导致多线程并发场景下 函数功能会出错。
- **反例**: 在工具类或者单例类等中，放置了非锁的数据结构，例如：时间戳，计数器等等，数据结构里面的内容与函数的上下文计算，特别说明，无论属性本身是否是线程安全的，都会有问题。
- **正例**: 多线程场景下类属性必须都使用不能带状态的数据结构（锁和常量例外），保证类能支持多线程并发安全。

### JAVA-CON-003: 禁止使用不安全的随机数生成器
- **检查锚点**: new Random(), Math.random()
- **正例**: SecureRandom sr = new SecureRandom();

## 性能优化

### JAVA-PERF-001: 禁止使用异常控制程序流程
- **检查锚点**: 使用异常控制流程, catch中return/break, 异常用于业务逻辑
- **反例**: try { if (condition) throw new Exception(); } catch { return; }
- **正例**: 使用条件判断而非异常控制流程

### JAVA-PERF-002: 禁止在循环中拼接字符串
- **检查锚点**: +拼接字符串在for/while/stream循环体内, String += 在循环中
- **反例**: for (String item : items) { result += item; }
- **正例**: StringBuilder sb = new StringBuilder(); for (String item : items) { sb.append(item); }

### JAVA-PERF-003: 禁止在循环中查询数据库
- **检查锚点**: 数据库查询方法(mapper.select, repository.find)在for/while/stream循环体内
- **反例**: for (Long id : ids) { User user = userMapper.selectById(id); }
- **正例**: List<User> users = userMapper.selectBatchIds(ids);

### JAVA-PERF-004: 禁止大循环内创建不必要的对象
- **检查锚点**: new对象在for/while高频循环体内, 循环内创建DateFormat/SimpleDateFormat
- **反例**: for (Item item : items) { DateFormat df = new SimpleDateFormat("yyyy-MM-dd"); }
- **正例**: DateTimeFormatter df = DateTimeFormatter.ofPattern("yyyy-MM-dd"); 在循环外创建

### JAVA-PERF-005: 选择合适的集合类型
- **检查锚点**: HashMap遍历, ArrayList频繁插入删除, 使用不当的集合类型
- **正例**: 按需选择：HashMap适合快速查找，LinkedList适合频繁插入删除

### JAVA-PERF-006: 禁止不当的循环和递归
- **检查锚点**: 嵌套循环复杂度高, 无限递归, 算法效率低
- **正例**: 优化算法复杂度，使用迭代替代递归

## 编码规范

### JAVA-CODE-001: 禁止使用Optional.of
- **检查锚点**: Optional.of(
- **反例**: Optional.of(value)
- **正例**: Optional.ofNullable(value)

### JAVA-CODE-002: 禁止直接修改SQL返回对象
- **检查锚点**: Mybatis查询结果.getXxxList().clear(), getXxxList().remove(), getXxxList().add()
- **反例**: trailPO.getNmsTrailPOList().clear();
- **正例**: trailPO.setNmsTrailPOList(Collections.emptyList());

### JAVA-CODE-003: 禁止使用java.text.SimpleDateFormat
- **检查锚点**: new SimpleDateFormat, SimpleDateFormat.parse, SimpleDateFormat.format
- **反例**: new SimpleDateFormat("yyyy-MM-dd").parse(dateStr);
- **正例**: DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");

### JAVA-CODE-004: 禁止使用mapstruct的expression
- **检查锚点**: @Mapping(expression=, expression中包含复杂逻辑
- **正例**: 复杂转换建议编码实现而非使用expression

### JAVA-CODE-005: 禁止使用Integer.parseInt
- **检查锚点**: Integer.parseInt(
- **反例**: Integer.parseInt(str);
- **正例**: Ints.tryParse(str) 或异常处理

### JAVA-CODE-006: 枚举转换禁止使用name()
- **检查锚点**: EnumType.name()用于转换, 枚举.name()后用于业务逻辑
- **反例**: String type = status.name();
- **正例**: String type = status.getCode();

### JAVA-CODE-007: 不信任数据源必须增加校验
- **检查锚点**: RPC请求的Response数据直接使用, Rest接口Request数据直接使用, 外部传入数据未判空
- **反例**: response.getData().getId();
- **正例**: if (response.getData() != null && response.getData().getId() != null)

### JAVA-CODE-008: 禁止手写重试框架
- **检查锚点**: 代码中有手写重试机制的场景，RetryCount,  Exception 中Sleep 继续这种场景使用Retry框架（RetryTemplate 或 注入的方式实现）
- **反例**: 重试机制，手写一份重试方案
- **正例**: 使用SpringRetry 或者 使用SpringRetry来完成

### JAVA-CODE-009: MyBatis动态SQL中连续字段更新时必须在末尾添加英文逗号
- **检查锚点**: MyBatis的trim标签内多个set字段, if test="${}!=null"多个连续字段
- **反例**: `<if>...encryptMode=#{item.encryptMode}</if><if>...negotiationMode=#{item.negotiationMode}</if>`（缺少逗号）
- **正例**: 每个非末尾字段添加逗号

### JAVA-CODE-010: 线程池配置错误

- **检查锚点**: 检查线程池的配置，1、配置Java的JDK的线程池，Core Size 的大小和Max Size的大小有差异，确认线程池队列的配置，如果queue size 大于10，那么就有问题，Max Size的配置会失效，2、如果Core size，Max Size配置都超过10 ，那么最好建议配置可以回收核心线程；
- **反例**: Java 代码使用JDK原生线程池，Core size =10, Max Size = 40, queue =2000  ,那么实际上Max的Size会失效。
- **正例**: Core size =10, Max Size = 10, queue =2000 ， 并且配置可以回收核心线程就好；或者 Core size =10, Max Size = 40, queue =10，queue 队列不大，Max size的配置也有意义；

## 架构设计

### JAVA-ARCH-001: 可枚举概念必须使用枚举定义
- **检查锚点**: 若干个常量定义同一概念(int/string常量组), if-else链判断枚举值
- **反例**: public static final int STATUS_ACTIVE = 1;
- **正例**: public enum Status { ACTIVE, INACTIVE; }

### JAVA-ARCH-002: 同步开销最小化
- **检查锚点**: 不当使用synchronized, 同步块过大, 过度同步
- **正例**: 缩小同步范围，使用ConcurrentHashMap等并发容器

