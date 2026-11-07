# Rust 检视规则

### RUST-SEC-001: 禁止unsafe块缺少安全论证注释
- **检查锚点**: unsafe {, unsafe fn, unsafe impl, 无SAFETY注释
- **反例**: `unsafe { ptr::copy(src, dst, len) }` — 无安全说明
- **正例**: `// SAFETY: src和dst有效且不重叠, len不超过分配大小` \n `unsafe { ptr::copy(src, dst, len) }`

### RUST-SEC-002: 禁止Command注入用户输入
- **检查锚点**: std::process::Command, .arg(拼接), .args(未校验), shell=True等效
- **反例**: `Command::new("sh").arg("-c").arg(user_input)`
- **正例**: `Command::new("tool").arg(validated_arg)` — 参数分离

### RUST-SEC-003: 禁止硬编码密钥和凭证
- **检查锚点**: password=, secret=, apiKey=, token=, const赋值敏感字符串, 连接字符串含密码

### RUST-SEC-004: 必须禁止整数溢出或显式处理
- **检查锚点**: as u32/as usize截断, wrapping_add, saturating_add, checked_add, 溢出未处理
- **反例**: `let size = len as usize` — 可能截断
- **正例**: `let size = usize::try_from(len).map_err(|_| "overflow")?`

### RUST-SEC-005: 禁止跳过TLS证书验证
- **检查锚点**: danger_accept_invalid_certs, accept_invalid_hostnames, tls_config跳过验证
- **反例**: `ClientBuilder::new().danger_accept_invalid_certs(true)`

### RUST-SEC-006: 必须防范TOCTOU竞态
- **检查锚点**: 先std::fs::metadata后std::fs::open, 先检查后操作模式, /tmp临时文件
- **反例**: `if path.exists() { fs::open(path) }` — TOCTOU
- **正例**: `fs::OpenOptions::new().write(true).create_new(true).open(path)` — 原子操作

### RUST-CON-001: 禁止Send/Sync违规
- **检查锚点**: unsafe impl Send, unsafe impl Sync, 跨线程传递Rc<>, 裸指针跨线程
- **反例**: `unsafe impl Send for MyStruct {}` — 无安全论证
- **正例**: 使用 Arc<Mutex<T>> 或 Arc<T>(T: Send+Sync)

### RUST-CON-002: 禁止Rc跨线程使用
- **检查锚点**: Rc<> 在spawn中, Rc<> 传递给thread, Arc与Rc混用
- **反例**: `thread::spawn(move || rc_cell.borrow())` — Rc非Send
- **正例**: 使用 `Arc<Mutex<T>>` 或 `Arc<T>`

### RUST-CON-003: 必须使用Mutex/RwLock保护共享可变状态
- **检查锚点**: static mut, UnsafeCell在多线程, 全局可变状态无锁保护
- **反例**: `static mut COUNTER: i32 = 0;` — 多线程不安全
- **正例**: `static COUNTER: AtomicI32 = AtomicI32::new(0);` 或 `Mutex`

### RUST-CON-004: 禁止死锁（锁顺序不一致）
- **检查锚点**: 多个Mutex同时持有, 嵌套lock(), 不同函数获取锁顺序不同
- **正例**: 统一锁获取顺序，或使用单一粗粒度锁

### RUST-CON-005: 必须正确使用原子操作的内存序
- **检查锚点**: Ordering::Relaxed用于同步, Ordering::SeqCst滥用, compare_exchange的Ordering
- **反例**: `flag.store(true, Ordering::Relaxed)` — 用于同步时Relaxed不够
- **正例**: `flag.store(true, Ordering::Release)` 配合 `Acquire` 读取

### RUST-CODE-001: 禁止unwrap/expect在可能失败场景
- **检查锚点**: .unwrap(), .expect( 在非确定性上下文, Option/Result直接unwrap
- **反例**: `file.read_to_end(&mut buf).unwrap()` — 可能失败
- **正例**: `file.read_to_end(&mut buf)?` 或 `match`/`if let` 处理

### RUST-CODE-002: 禁止在库代码中panic
- **检查锚点**: panic!, unimplemented!, todo!, 除零, 索引越界, unwrap在lib中
- **反例**: `panic!("unexpected value")` — 库代码中
- **正例**: `return Err(MyError::UnexpectedValue)` — 返回Result

### RUST-CODE-003: 必须使用?运算符传播错误
- **检查锚点**: match Err分支return Err(e), 手动错误传播, .map_err后return
- **反例**: `match result { Ok(v) => v, Err(e) => return Err(e) }`
- **正例**: `let v = result?;`

### RUST-CODE-004: 禁止不必要的clone
- **检查锚点**: .clone() 在可借用场景, &可替代owned值, Rc::clone不必要的引用计数
- **反例**: `fn process(data: &Vec<u8>) { inner(data.clone()) }` — 内层可接受&
- **正例**: `fn process(data: &Vec<u8>) { inner(data) }` — 传递引用

### RUST-CODE-005: 必须处理Result的所有变体
- **检查锚点**: match缺Err分支, if let Ok但忽略Err, _通配符吞掉错误
- **反例**: `if let Ok(val) = risky_op() { use(val) }` — Err被忽略
- **正例**: `match risky_op() { Ok(val) => use(val), Err(e) => handle(e) }`

### RUST-CODE-006: 必须保证match穷尽性
- **检查锚点**: match缺分支, _通配符掩盖新变体, 非穷尽enum匹配
- **反例**: `match opt { Some(v) => v }` — 缺None
- **正例**: `match opt { Some(v) => v, None => default }` 或 `#![deny(unreachable_patterns)]`

### RUST-CODE-007: 禁止RefCell运行时借用冲突
- **检查锚点**: RefCell<>, borrow_mut+borrow同时, try_borrow, 运行时panic
- **反例**: `let r = cell.borrow(); cell.borrow_mut();` — panic
- **正例**: 设计上避免运行时可变借用，或使用 `try_borrow_mut`

### RUST-PERF-001: 禁止不必要的堆分配
- **检查锚点**: String代替&str, Vec代替&[T], Box代替栈分配, to_string()在可借用处
- **反例**: `fn name() -> String { "hello".to_string() }` — 每次分配
- **正例**: `fn name() -> &'static str { "hello" }` — 零分配

### RUST-PERF-002: 必须预分配Vec/String容量
- **检查锚点**: Vec::new()+push循环, String::new()+push_str循环, Vec::with_capacity缺失
- **反例**: `let mut v = Vec::new(); for i in 0..1000 { v.push(i) }`
- **正例**: `let mut v = Vec::with_capacity(1000); for i in 0..1000 { v.push(i) }`

### RUST-PERF-003: 禁止在热路径中反复编译正则
- **检查锚点**: Regex::new在函数内, regex!宏缺失, lazy_static!缺失
- **反例**: `fn is_match(s: &str) { Regex::new(r"\d+").unwrap().is_match(s) }`
- **正例**: `static RE: Lazy<Regex> = Lazy::new(|| Regex::new(r"\d+").unwrap());`

### RUST-PERF-004: 禁止N+1数据库查询
- **检查锚点**: 循环中sqlx::query, 循环中diesel查询, 批量操作拆成单条
- **反例**: `for id in ids { sqlx::query("SELECT ... WHERE id=$1").bind(id).fetch_one(&pool) }`
- **正例**: `sqlx::query("SELECT ... WHERE id = ANY($1)").bind(ids).fetch_all(&pool)`

### RUST-PERF-005: 必须选择正确的智能指针
- **检查锚点**: Box<>(单所有权堆), Rc<>(单线程共享), Arc<>(多线程共享), 误用场景
- **反例**: 单线程用 `Arc<Mutex<T>>` — Arc原子开销无意义
- **正例**: 单线程用 `Rc<RefCell<T>>`，跨线程用 `Arc<Mutex<T>>`

### RUST-ARCH-001: 禁止库类型暴露具体错误实现
- **检查锚点**: pub fn返回thiserror具体类型, 错误类型未做抽象, 库暴露内部错误
- **正例**: 库定义 `enum Error { ... }` 实现_std::error::Error，应用层可用 anyhow

### RUST-ARCH-002: 必须使用trait做抽象而非具体类型
- **检查锚点**: 函数参数为具体struct, 直接依赖实现细节, dyn Trait vs impl Trait
- **反例**: `fn save(repo: PostgresRepo)`
- **正例**: `fn save(repo: &dyn Repository)` 或 `fn save<R: Repository>(repo: &R)`
