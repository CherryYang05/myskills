# Go 检视规则

### GO-SEC-001: 禁止SQL拼接注入
- **检查锚点**: fmt.Sprintf+SQL, string concatenation+SQL, db.Query+拼接, db.Exec+拼接
- **反例**: `db.Query(fmt.Sprintf("SELECT * FROM users WHERE id=%s", userID))`
- **正例**: `db.Query("SELECT * FROM users WHERE id=$1", userID)`

### GO-SEC-002: 禁止os/exec注入未校验输入
- **检查锚点**: exec.Command, exec.CommandContext, CombinedOutput, args拼接
- **反例**: `exec.Command("sh", "-c", userInput)`
- **正例**: `exec.Command("tool", validatedArg)` — 参数分离

### GO-SEC-003: 禁止硬编码密钥和凭证
- **检查锚点**: password=, secret=, apiKey=, token=, 连接字符串含密码, const赋值敏感值

### GO-SEC-004: 禁止使用不安全随机数生成器
- **检查锚点**: math/rand, rand.Int, rand.Seed, rand.Read
- **反例**: `token := fmt.Sprintf("%d", rand.Int())` — 可预测
- **正例**: `crypto/rand`, `crypto/rand.Read`

### GO-SEC-005: 必须对用户输入做校验
- **检查锚点**: r.URL.Query(), r.FormValue(), r.Header.Get(), template.HTML
- **反例**: `template.HTML(userInput)` — XSS
- **正例**: 使用 text/template 自动转义

### GO-SEC-006: 禁止跳过TLS证书验证
- **检查锚点**: InsecureSkipVerify: true, tls.Config{InsecureSkipVerify: true}
- **反例**: `&tls.Config{InsecureSkipVerify: true}`

### GO-SEC-007: 必须使用安全密码哈希
- **检查锚点**: md5.Sum, sha1.Sum, crypto/md5, crypto/sha1用于密码
- **反例**: `md5.Sum([]byte(password))`
- **正例**: `bcrypt.GenerateFromPassword()` 或 `argon2.IDKey()`

### GO-SEC-008: 必须防范SSRF
- **检查锚点**: http.Get+用户URL, http.NewRequest+用户URL, url.Parse未校验scheme/host
- **反例**: `http.Get(userProvidedURL)`
- **正例**: 校验URL scheme为https、host在白名单内

### GO-CON-001: 禁止并发读写原生map
- **检查锚点**: map[...] 在多个goroutine中读写, 无sync.RWMutex保护
- **反例**: `go func() { m[key] = val }()` — 同时另一goroutine读m
- **正例**: `sync.RWMutex` 保护 或 `sync.Map`

### GO-CON-002: 必须使用sync.WaitGroup或errgroup等待goroutine完成
- **检查锚点**: go func() 但无WaitGroup.Add/Done, 主goroutine不等待
- **反例**: `go doWork()` — 不等待完成
- **正例**: `wg.Add(1); go func() { defer wg.Done(); doWork() }(); wg.Wait()`

### GO-CON-003: 必须使用context控制goroutine生命周期
- **检查锚点**: go func() 无context参数, time.Sleep在goroutine中, 无取消机制
- **反例**: `go func() { for { doWork() } }()` — 无法停止
- **正例**: `go func(ctx context.Context) { for { select { case <-ctx.Done(): return; default: doWork() } } }(ctx)`

### GO-CON-004: 禁止goroutine泄漏
- **检查锚点**: go func()中channel永远阻塞, 无context取消, 无done channel
- **反例**: `go func() { ch <- val }()` — 无人消费ch则泄漏
- **正例**: 使用 `select case <-ctx.Done()` 退出

### GO-CON-005: 必须使用defer关闭资源
- **检查锚点**: os.Open, os.Create, net.Dial, rows.Next 无defer Close
- **反例**: `f, _ := os.Open(path)` — 无 `defer f.Close()`
- **正例**: `f, err := os.Open(path); if err != nil { ... }; defer f.Close()`

### GO-CODE-001: 必须处理所有error返回值
- **检查锚点**: `_ =`, `if err != nil`缺失, 忽略error赋值, db.Exec无错误检查
- **反例**: `f, _ := os.Open(path)`
- **正例**: `f, err := os.Open(path); if err != nil { return err }`

### GO-CODE-002: 必须使用%w包装错误保留上下文
- **检查锚点**: fmt.Errorf("...%v", err), errors.New丢失原始err
- **反例**: `fmt.Errorf("failed to open: %v", err)` — 丢失链
- **正例**: `fmt.Errorf("failed to open: %w", err)` — 保留链可Unwrap

### GO-CODE-003: 禁止type assertion不加ok检查
- **检查锚点**: v.(Type) 无 ,ok, interface{}断言
- **反例**: `str := v.(string)` — 若v非string则panic
- **正例**: `str, ok := v.(string); if !ok { ... }`

### GO-CODE-004: 禁止空select语句永久阻塞
- **检查锚点**: `select {}`, 无case的select
- **反例**: `select {}` — 永久阻塞goroutine

### GO-CODE-005: 禁止滥用全局变量
- **检查锚点**: var在包级别声明mutable状态, 全局map, 全局slice
- **正例**: 使用结构体封装状态，通过方法访问

### GO-CODE-006: 禁止使用init()做复杂逻辑
- **检查锚点**: func init(), init()中网络调用、文件操作、panic
- **正例**: init()仅用于简单注册，复杂逻辑放显式初始化函数

### GO-PERF-001: 禁止在循环中拼接字符串
- **检查锚点**: += 在for循环中, fmt.Sprintf在循环中拼接
- **反例**: `for _, s := range items { result += s }`
- **正例**: `var b strings.Builder; for _, s := range items { b.WriteString(s) }`

### GO-PERF-002: 必须预分配slice容量
- **检查锚点**: append在已知长度循环中无make预分配, []T{}后循环append
- **反例**: `var items []int; for i := 0; i < n; i++ { items = append(items, i) }`
- **正例**: `items := make([]int, 0, n); for i := 0; i < n; i++ { items = append(items, i) }`

### GO-PERF-003: 禁止在热路径中反复编译正则
- **检查锚点**: regexp.MustCompile在函数内, regexp.Compile在循环/热路径
- **反例**: `func match(s string) { re := regexp.MustCompile("\\d+"); ... }`
- **正例**: `var re = regexp.MustCompile("\\d+"); func match(s string) { re.MatchString(s) }`

### GO-PERF-004: 禁止N+1数据库查询
- **检查锚点**: 循环中db.Query, 循环中rows.Next+内层查询, GORM Preload缺失
- **反例**: `for _, id := range ids { db.Query("SELECT ... WHERE id=$1", id) }`
- **正例**: `db.Query("SELECT ... WHERE id = ANY($1)", ids)` — 批量查询

### GO-PERF-005: 必须对高频I/O使用bufio缓冲
- **检查锚点**: os.File.Read小buffer, net.Conn.Read无bufio, fmt.Fprint循环
- **反例**: `conn.Write([]byte("a")); conn.Write([]byte("b"))` — 多次系统调用
- **正例**: `w := bufio.NewWriter(conn); w.WriteString("a"); w.Flush()`

### GO-ARCH-001: 必须使用接口解耦依赖
- **检查锚点**: 函数参数为具体结构体, 直接依赖数据库结构体, new具体实现
- **反例**: `func Process(db *sql.DB)`
- **正例**: `func Process(db DataAccessor)` — 接口参数

### GO-ARCH-002: 禁止循环依赖包
- **检查锚点**: import A→B→A, 循环import编译错误
- **正例**: 提取公共接口到独立包，依赖方向单向
