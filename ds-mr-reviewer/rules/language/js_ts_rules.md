# JavaScript & TypeScript 检视规则

### JSTS-SEC-001: 禁止使用innerHTML/dangerouslySetInnerHTML渲染用户输入
- **检查锚点**: innerHTML, dangerouslySetInnerHTML, outerHTML, insertAdjacentHTML
- **反例**: `element.innerHTML = userInput`
- **正例**: `element.textContent = userInput` 或 DOMPurify.sanitize

### JSTS-SEC-002: 禁止使用eval/Function/setTimeout字符串参数
- **检查锚点**: eval(, new Function(, setTimeout(string,, setInterval(string,
- **反例**: `eval("var x = " + userInput)`
- **正例**: 使用 JSON.parse 解析数据，函数引用替代字符串

### JSTS-SEC-003: 禁止child_process注入用户输入
- **检查锚点**: child_process.exec, child_process.spawn, execSync, execFile+拼接
- **反例**: `exec("ls " + userDir)`
- **正例**: `execFile("ls", [userDir])` — 参数分离

### JSTS-SEC-004: 禁止硬编码密钥和凭证到前端代码
- **检查锚点**: apiKey=, secret=, password=, token=, Bearer+硬编码, .env推送到前端
- **反例**: `const API_KEY = "sk-abc123"` 在前端代码中

### JSTS-SEC-005: 必须对Cookie设置安全属性
- **检查锚点**: document.cookie=, Set-Cookie, cookie.serialize, SameSite, HttpOnly, Secure
- **反例**: `document.cookie = "token=" + jwt` — 无安全属性
- **正例**: 服务端 `Set-Cookie: token=xxx; HttpOnly; Secure; SameSite=Strict`

### JSTS-SEC-006: 禁止原型污染
- **检查锚点**: Object.assign({}, untrusted), merge(, deepMerge+untrusted, __proto__, constructor.prototype
- **反例**: `Object.assign(target, JSON.parse(userInput))`
- **正例**: 使用 Map 或 `Object.create(null)` + 白名单字段

### JSTS-SEC-007: 禁止fs路径拼接未校验用户输入
- **检查锚点**: path.join+用户输入, fs.readFile+用户路径, ../在路径中
- **反例**: `fs.readFile(path.join(baseDir, userInput))`
- **正例**: `path.resolve(baseDir, userInput).startsWith(baseDir)` — 校验逃逸

### JSTS-CON-001: 禁止未处理的Promise拒绝
- **检查锚点**: .then()无.catch, async函数无try-catch, unhandledRejection
- **反例**: `fetch(url).then(r => r.json())` — 无catch
- **正例**: `fetch(url).then(r => r.json()).catch(handleError)` 或 try-catch

### JSTS-CON-002: 必须在useEffect中清理副作用
- **检查锚点**: useEffect无return清理函数, setInterval/setTimeout无clearTimeout, addEventListener无removeEventListener
- **反例**: `useEffect(() => { timer = setInterval(fn, 1000) }, [])` — 不清理
- **正例**: `useEffect(() => { const id = setInterval(fn, 1000); return () => clearInterval(id) }, [])`

### JSTS-CON-003: 禁止RxJS订阅泄漏
- **检查锚点**: .subscribe(无unsubscribe, 无takeUntil, 无async pipe, Subscription未清理
- **反例**: `this.service.getData().subscribe(data => ...)` — 不取消
- **正例**: `this.service.getData().pipe(takeUntil(this.destroy$)).subscribe(...)`

### JSTS-CODE-001: 禁止使用==做隐式类型转换比较
- **检查锚点**: ==, != (非===, !==)
- **反例**: `if (value == "1")`
- **正例**: `if (value === "1")`

### JSTS-CODE-002: 禁止在TypeScript中使用any类型
- **检查锚点**: : any, as any, <any>, @ts-ignore, @ts-nocheck
- **反例**: `function process(data: any) { ... }`
- **正例**: `function process(data: UserData) { ... }`

### JSTS-CODE-003: 必须启用TypeScript严格模式
- **检查锚点**: strictNullChecks, noImplicitAny, strict, tsconfig.json
- **正例**: `tsconfig.json: { "compilerOptions": { "strict": true } }`

### JSTS-CODE-004: 禁止useEffect依赖数组不完整
- **检查锚点**: useEffect依赖列表缺失引用变量, eslint react-hooks/exhaustive-deps
- **反例**: `useEffect(() => { fetchData(id) }, [])` — 缺id依赖
- **正例**: `useEffect(() => { fetchData(id) }, [id])`

### JSTS-CODE-005: 禁止保留console.log/debugger语句
- **检查锚点**: console.log, console.debug, debugger, console.warn(非错误场景)
- **正例**: 使用日志库，生产构建自动去除

### JSTS-CODE-006: 必须为React列表提供稳定key
- **检查锚点**: .map(无key, key=index, key={Math.random()}
- **反例**: `<li key={index}>`
- **正例**: `<li key={item.id}>`

### JSTS-CODE-007: 禁止使用var声明变量
- **检查锚点**: var (非let/const)
- **正例**: `const` 不可变，`let` 可变，禁止 `var`

### JSTS-CODE-008: 必须处理null/undefined使用可选链
- **检查锚点**: obj.prop.prop2 链式访问无?, && 嵌套判空
- **反例**: `user && user.address && user.address.city`
- **正例**: `user?.address?.city`

### JSTS-PERF-001: 禁止在循环中进行DOM操作
- **检查锚点**: 循环内innerHTML+=, 循环内appendChild, 循环内setState触发re-render
- **反例**: `items.forEach(i => { container.innerHTML += `<div>${i}</div>` })`
- **正例**: `container.innerHTML = items.map(i => `<div>${i}</div>`).join('')`

### JSTS-PERF-002: 禁止同步文件系统操作
- **检查锚点**: fs.readFileSync, fs.writeFileSync, fs.mkdirSync 在请求处理路径
- **反例**: `const data = fs.readFileSync(path)` — 阻塞事件循环
- **正例**: `const data = await fs.promises.readFile(path)`

### JSTS-PERF-003: 必须对高频事件使用防抖或节流
- **检查锚点**: onscroll, onresize, oninput, onmousemove 直接绑定处理函数无debounce/throttle
- **反例**: `window.addEventListener('scroll', handleScroll)`
- **正例**: `window.addEventListener('scroll', debounce(handleScroll, 100))`

### JSTS-PERF-004: 禁止N+1数据库/API查询
- **检查锚点**: 循环中await查询, 循环中fetch, map+await串行
- **反例**: `for (const id of ids) { await fetch(`/api/item/${id}`) }`
- **正例**: `await Promise.all(ids.map(id => fetch(`/api/item/${id}`)))` 或批量接口

### JSTS-PERF-005: 必须对React纯组件使用memo/useMemo/useCallback
- **检查锚点**: 子组件re-render但props未变, 对象/数组props每次新建, 函数props内联定义
- **反例**: `<Child onClick={() => handleClick()} items={[1,2,3]} />`
- **正例**: `const onClick = useCallback(handleClick, []); const items = useMemo(() => [1,2,3], [])`

### JSTS-ARCH-001: 必须使用依赖注入而非硬编码import具体实现
- **检查锚点**: 直接import数据库实现, new具体类在业务逻辑中, import的具体服务不可替换
- **正例**: 接口定义 + Context/Provider注入实现

### JSTS-ARCH-002: 禁止Prop Drilling超过3层
- **检查锚点**: 连续3+层组件透传props, 中间组件仅做透传
- **正例**: 使用 Context, Zustand, Jotai 等状态管理
