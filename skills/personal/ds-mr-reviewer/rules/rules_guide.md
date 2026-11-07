# 检视规则（Rules）指南

本指南阐述 MR 代码检视规则（Rules）的结构化编写规范和使用方法。

## 目录结构

```
rules/
├── common_rules.md                          # 通用检视规则（所有MR必守）
├── language/                                # 按编程语言分组的特定检视规则
│   ├── java_rules.md
│   ├── python_rules.md
│   ├── c_rules.md
│   ├── cpp_rules.md
│   ├── csharp_rules.md
│   ├── go_rules.md
│   ├── rust_rules.md
│   └── js_ts_rules.md
└── mr_reviewer_tips.md.example              # 代码仓级检视规则编写示例
```

## 规则应用顺序

当进行MR代码检视时，AI模型按以下顺序读取和应用规则：

1. **通用规则**: 读取 `common_rules.md`
2. **代码仓根目录检视规则**: 在被检视代码仓根目录下搜索检视规则文件
   - 优先查找 `mr_reviewer_rules.md`（新命名）
   - 若不存在，回退查找 `mr_reviewer_tips.md`（兼容旧仓）
   - 如果文件中定义了 `link_repo` 元数据，系统会自动加载所声明的其他代码仓的检视规则
3. **Linked Repo 规则**: 递归加载 `link_repo` 声明的所有代码仓的检视规则
   - 支持多层递归引用
   - 自动检测并避免循环引用
4. **语言特定规则**: 根据diff中的文件扩展名，读取对应语言的规则
    - Java文件 (.java) → `language/java_rules.md`
    - Python文件 (.py) → `language/python_rules.md`
    - C++文件 (.cpp, .cc, .h, .hpp) → `language/cpp_rules.md`
    - C文件 (.c, .h) → `language/c_rules.md`
    - C#文件 (.cs) → `language/csharp_rules.md`
    - Go文件 (.go) → `language/go_rules.md`
    - Rust文件 (.rs) → `language/rust_rules.md`
    - JavaScript/TypeScript文件 (.js, .jsx, .ts, .tsx) → `language/js_ts_rules.md`

**规则遵守**: 所有来源的规则均需同时遵守，AI会综合应用所有检视规则进行代码检视

## 结构化规则格式规范

### 必填字段（3个）

| key | 中文属性名 | 说明 | 示例 |
|-----|-----------|------|------|
| `rule_id` | 规则编号 | 唯一标识。AI遍历时逐条报告"已检查 XXX"，杜绝遗漏 | `JAVA-SEC-001` |
| `title` | 规则标题 | 一句话命令式描述，说明要检查什么 | `禁止使用未参数化的SQL拼接` |
| `checkpoint` | 检查锚点 | AI重点扫描的关键字/代码模式/代码结构，指导AI如何定位可疑代码 | `String.format用于SQL, +拼接SQL字符串` |

### 可选字段（2个）

| key | 中文属性名 | 说明 | 示例 |
|-----|-----------|------|------|
| `sample_bad` | 反例 | 不好的代码片段 | `String sql = "SELECT * FROM user WHERE id=" + userId;` |
| `sample_good` | 正例 | 推荐的代码片段 | `PreparedStatement ps = conn.prepareStatement("SELECT * FROM user WHERE id=?");` |

### Markdown 中的呈现格式

每条规则以 `### 规则编号: 规则标题` 作为锚点开头，后跟各字段以中文属性名标注：

```markdown
### JAVA-SEC-001: 禁止使用未参数化的SQL拼接
- **检查锚点**: String.format用于SQL, +拼接SQL字符串, Statement.executeQuery(拼接字符串)
- **反例**: `String sql = "SELECT * FROM user WHERE id=" + userId;`
- **正例**: `PreparedStatement ps = conn.prepareStatement("SELECT * FROM user WHERE id=?");`
```

### 字段编写要求

- **规则编号**: 必须全局唯一，遵循 Rule ID 编号规范（见下文）
- **规则标题**: 使用命令式语言（"禁止X"、"必须Y"、"检查Z"），避免描述性语言
- **检查锚点**: 这是解决"AI不知道怎么检查"的核心字段。必须给出AI可扫描的具体关键字、函数名、API名、代码模式，多个锚点用逗号分隔。不要写泛泛的描述

## Rule ID 编号规范

### 格式

```
{前缀}-{分类}-{序号}
```

### 前缀（按规则来源）

| 规则来源 | 前缀 | 示例 |
|---------|------|------|
| 语言级规则 | 语言名大写 | `JAVA-SEC-001`, `CPP-MEM-012`, `PY-SEC-003` |
| 代码仓级规则 | `BIZ` | `BIZ-001`, `BIZ-012` |
| 通用级规则 | `COM` | `COM-001` |

### 语言级的领域分类缩写

| 分类缩写 | 分类名称 | 含义 | 典型规则示例 |
|---------|---------|------|------------|
| SEC | 安全合规 | SQL注入、命令注入、信息泄露、硬编码密码等 | 禁止使用未参数化的SQL, 禁止硬编码密码 |
| MEM | 内存管理 | 内存泄漏、非法访问、指针安全、资源未释放等 | malloc后必须判空, 禁止裸指针管理内存 |
| CON | 并发安全 | 竞态条件、死锁、线程安全、共享资源无锁等 | 禁止对共享可变状态无同步访问 |
| CODE | 编码规范 | 命名合规、魔术数字、异常处理、代码风格等 | 禁止使用Optional.of, 禁止直接修改SQL返回对象 |
| PERF | 性能优化 | N+1查询、循环创建对象、不必要的拷贝、算法复杂度等 | 禁止循环中拼接字符串, 禁止循环中查询数据库 |
| ARCH | 架构设计 | 耦合度、接口设计、模块职责、抽象层次等 | 优先使用智能指针而非原始指针 |

### 编号规则

- 序号为三位数字，从001开始
- 同前缀+分类内递增（如 JAVA-SEC-001, JAVA-SEC-002, JAVA-CODE-001）
- 代码仓级和通用级不分类，直接 BIZ-序号 / COM-序号
- 不同语言相同领域的规则可以有不同的编号（JAVA-SEC-001 和 CPP-SEC-001 是不同规则）

## 代码仓级检视规则编写规范

### 文件位置

代码仓根目录 → `mr_reviewer_rules.md`（推荐）或 `mr_reviewer_tips.md`（兼容旧仓）

> 系统优先查找 `mr_reviewer_rules.md`，若不存在则回退查找 `mr_reviewer_tips.md`。新代码仓建议使用 `mr_reviewer_rules.md`。

### 元数据配置

文件开头支持YAML格式的元数据配置：

```yaml
---
link_repo: TransNeWebService,TransFrontendService
---
```

**配置项说明：**

- `link_repo`（可选）: 声明当前代码仓需要遵循的其他代码仓的检视规则，多个仓库用英文逗号分隔
- `depend_repo`（可选）: 声明当前代码仓的代码可能会调用到的其他仓库，多个仓库用英文逗号分隔，用于代码搜索

**link_repo 使用示例：**

```yaml
---
link_repo: NCE-T/TransNeWebService,NCE-T/TransFrontendService
---
```

**depend_repo 使用示例：**

```yaml
---
depend_repo: NCE-T/TransNeWebService,NCE-T/TransFrontendService
---
```

### link_repo vs depend_repo 的区别

- `link_repo`: 加载其他仓库的检视规则，不涉及代码搜索
- `depend_repo`: 代码搜索时扩展到其他仓库，规则检查和调用链分析时搜索

### 规则内容

在元数据配置之后，编写当前代码仓特有的检视规则：

```markdown
---
link_repo: xxx
depend_repo: xxx
---

# MR Reviewer Rules

本文件为代码仓的MR检视规则配置文件，放置于代码仓根目录，以下所有检视规则必须遵守。

### BIZ-001: 设置策略属性时必须验证业务前提条件
- **检查锚点**: setXxxPolicy, fillXxxPolicy, 策略属性赋值语句
- **反例**: `service.setOsuDispatchPolicy(policy);`
- **正例**: `if (underTransType == OSU) { service.setOsuDispatchPolicy(policy); }`
```

## 添加新规则

### 添加语言规则

1. 在 `language/` 目录下编辑对应的 `{language}_rules.md` 文件
2. 按结构化格式添加新规则，分配唯一的 rule_id
3. 确保检查锚点具体、可操作

### 添加代码仓规则

在代码仓根目录下编辑 `mr_reviewer_rules.md`（或 `mr_reviewer_tips.md`）文件：
1. 按 BIZ-序号 分配规则编号
2. 此文件应纳入代码仓库的版本管理，规则的变更会随代码一起被追溯

## 规则使用场景

这些检视规则在MR代码检视中被用于：

1. **AI深度分析参考**：AI模型在分析代码变更时，会读取对应语言的规则文件，作为风险识别的重要参考
2. **语言特定风险识别**：根据修改文件的编程语言，动态加载对应的检视规则
3. **代码仓特定规则**：通过代码仓根目录的检视规则文件和link_repo配置，加载代码仓特有的业务规则
4. **逐条遍历检视**：AI按 rule_id 逐条检视，输出"已检查 XXX：通过/违规"，杜绝遗漏

## 最佳实践

1. **检查锚点必须具体可扫描**：给出具体的API名、函数名、关键字，不要写泛泛的描述
2. **规则标题使用命令式语言**：使用"禁止"、"必须"、"检查"等明确用语
3. **提供示例**：对于复杂规则，提供反例和正例代码示例
4. **精炼规则数量**：每种语言保持20-30条核心规则，宁缺毋滥
5. **定期更新规则**：随着代码演进和业务发展，及时更新检视规则
6. **版本化管理**：规则文件的变更也应该有清晰的commit message，便于追溯
7. **合理使用link_repo**：只声明真正需要共享规则的代码仓，避免过度引用

## 注意事项

- 规则文件必须使用UTF-8编码
- 每条规则必须能够被AI模型通过检查锚点定位和检查
- 文件名应为英文，避免使用中文和特殊字符
- 代码仓级检视规则文件应纳入代码仓库管理，规则变更会随代码版本追溯
- 语言特定规则、代码仓级规则和linked repo的规则需同时遵守
- link_repo支持递归引用，系统会自动检测循环引用并跳过
