# C# 检视规则

### CS-SEC-001: 禁止SQL拼接注入
- **检查锚点**: string.Concat, $""+SQL, string.Format+SQL, SqlCommand+拼接字符串
- **反例**: `new SqlCommand("SELECT * FROM Users WHERE Id=" + userId)`
- **正例**: `new SqlCommand("SELECT * FROM Users WHERE Id=@Id")` 配合 Parameters.AddWithValue

### CS-SEC-002: 禁止Process.Start注入未校验输入
- **检查锚点**: Process.Start, ProcessStartInfo, Arguments=
- **反例**: `Process.Start("cmd", "/c " + userInput)`
- **正例**: 使用参数列表并校验白名单

### CS-SEC-003: 禁止硬编码密钥和凭证
- **检查锚点**: password=, secret=, apiKey=, token=, 连接字符串含密码, hardcoded string literal赋值给敏感变量

### CS-SEC-004: 禁止使用不安全反序列化器
- **检查锚点**: BinaryFormatter, NetDataContractSerializer, SoapFormatter, LosFormatter
- **反例**: `new BinaryFormatter().Deserialize(stream)`
- **正例**: 使用 System.Text.Json 或 JsonSerializer

### CS-SEC-005: 必须对用户输入做校验和编码
- **检查锚点**: Request.Form, Request.QueryString, HttpContext.User, Razor @Html.Raw
- **反例**: `@Html.Raw(userInput)` — XSS
- **正例**: `@Html.DisplayFor(m => m.UserInput)` — 自动编码

### CS-SEC-006: 禁止禁用TLS/SSL验证
- **检查锚点**: ServicePointManager.ServerCertificateValidationCallback, HttpClientHandler.ServerCertificateCustomValidationCallback, return true
- **反例**: `ServerCertificateValidationCallback = (s,c,h,e) => true`

### CS-SEC-007: 必须使用安全密码哈希
- **检查锚点**: MD5.Create, SHA1.Create, MD5CryptoServiceProvider, SHA1Managed
- **反例**: `MD5.Create().ComputeHash(passwordBytes)`
- **正例**: 使用 Rfc2898DeriveBytes (PBKDF2) 或 BCrypt

### CS-SEC-008: 必须防范XXE攻击
- **检查锚点**: XmlReader, XmlTextReader, XmlDocument, XmlSerializer
- **反例**: `new XmlDocument() { ProhibitDtd = false }`
- **正例**: `XmlReaderSettings { DtdProcessing = DtdProcessing.Prohibit }`

### CS-SEC-009: 必须设置Cookie安全属性
- **检查锚点**: HttpCookie, CookieOptions, SameSite, HttpOnly, Secure
- **反例**: `new HttpCookie("auth") { Value = token }` 缺少 HttpOnly/Secure
- **正例**: `new HttpCookie("auth") { HttpOnly = true, Secure = true, SameSite = SameSiteMode.Strict }`

### CS-CON-001: 禁止并发访问非线程安全集合
- **检查锚点**: Dictionary<,>, List<>, HashSet<> 在多线程上下文中使用
- **正例**: ConcurrentDictionary, ConcurrentBag, 或加 lock

### CS-CON-002: 必须使用lock或Monitor保护共享可变状态
- **检查锚点**: static可变字段, 共享mutable对象, Interlocked, Monitor.Enter
- **反例**: 多线程直接读写 static List<>
- **正例**: `lock(_syncObj) { sharedList.Add(item); }`

### CS-CON-003: 禁止async/await死锁
- **检查锚点**: .Result, .Wait(), Task.GetAwaiter().GetResult() 在ASP.NET非Core上下文
- **反例**: `var result = GetDataAsync().Result` — 死锁
- **正例**: `var result = await GetDataAsync()` — 全链路异步

### CS-CON-004: 必须使用CancellationToken取消长时间异步任务
- **检查锚点**: Task.Run, Task.Delay, HttpClient.GetAsync 无CancellationToken参数
- **反例**: `await Task.Delay(Timeout.Infinite)`
- **正例**: `await Task.Delay(timeout, cancellationToken)`

### CS-CON-005: 必须使用using或Dispose释放资源
- **检查锚点**: IDisposable, Stream, HttpClient, SqlConnection, FileStream 无using
- **反例**: `var stream = new FileStream(...)` — 无using
- **正例**: `using var stream = new FileStream(...)`

### CS-CODE-001: 禁止使用==比较浮点数
- **检查锚点**: double==, float==, decimal==, ==
- **反例**: `if (price == 0.1)`
- **正例**: `if (Math.Abs(price - 0.1) < epsilon)`

### CS-CODE-002: 禁止忽略Task返回值
- **检查锚点**: 方法返回Task但调用处未await, _ = SomeAsync(), fire-and-forget
- **反例**: `SendEmailAsync();` — 未await
- **正例**: `await SendEmailAsync();` 或 `_ = SendEmailAsync();` 并显式处理异常

### CS-CODE-003: 必须启用Nullable Reference Types
- **检查锚点**: #nullable enable, nullable, Nullable, !操作符
- **正例**: 项目级别 `<Nullable>enable</Nullable>`

### CS-CODE-004: 禁止在迭代中修改集合
- **检查锚点**: foreach内调用.Add, .Remove, .Clear, List<>修改
- **反例**: `foreach(var item in list) { list.Remove(item); }`
- **正例**: `list.RemoveAll(item => condition)`

### CS-CODE-005: 禁止捕获异常后不做任何处理
- **检查锚点**: catch(Exception) { } , catch无处理逻辑
- **反例**: `catch { }`
- **正例**: `catch (Exception ex) { _logger.LogError(ex, "..."); throw; }`

### CS-CODE-006: 必须使用StringComparison进行字符串比较
- **检查锚点**: string.Equals, string.Compare, ToUpper/ToLower用于比较
- **反例**: `str1.ToLower() == str2.ToLower()`
- **正例**: `string.Equals(str1, str2, StringComparison.OrdinalIgnoreCase)`

### CS-PERF-001: 禁止在循环中拼接字符串
- **检查锚点**: += 在for/foreach/while中, String.Concat在循环
- **反例**: `for(...) { result += item; }`
- **正例**: `var sb = new StringBuilder(); for(...) { sb.Append(item); }`

### CS-PERF-002: 禁止N+1数据库查询
- **检查锚点**: EF Core: 循环中调用.ToList, .FirstOrDefault, .SaveChanges, Include缺失
- **反例**: `foreach(var order in orders) { var items = _ctx.Items.Where(i => i.OrderId == order.Id).ToList(); }`
- **正例**: `_ctx.Orders.Include(o => o.Items).ToList()` 或批量查询

### CS-PERF-003: 禁止不必要的装箱拆箱
- **检查锚点**: ArrayList, Hashtable, object参数传值类型, Enum.GetName在热路径
- **正例**: 使用泛型集合 List<int>, Dictionary<TKey, TValue>

### CS-PERF-004: 必须对只读查询使用AsNoTracking
- **检查锚点**: DbContext查询无AsNoTracking, ChangeTracker.AutoDetectChangesEnabled
- **反例**: `_ctx.Users.Where(u => u.Active).ToList()` — 无跟踪
- **正例**: `_ctx.Users.AsNoTracking().Where(u => u.Active).ToList()`

### CS-ARCH-001: 必须使用依赖注入而非直接new依赖
- **检查锚点**: new HttpClient(), new SqlConnection() 在业务逻辑中, ServiceLocator
- **正例**: 构造函数注入 `public MyService(IHttpClientFactory clientFactory)`

### CS-ARCH-002: 禁止硬编码配置值
- **检查锚点**: 连接字符串硬编码, 超时时间硬编码, URL硬编码
- **正例**: 使用 IOptions<T>, appsettings.json, 环境变量
