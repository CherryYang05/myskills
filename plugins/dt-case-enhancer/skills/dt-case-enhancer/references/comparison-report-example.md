# 已覆盖场景对比报告示例

本文档提供了"已覆盖场景对比报告"的完整示例,展示如何详细说明存量用例如何覆盖全量场景。

## 示例场景

假设我们正在为 `link_subhealth` 模块进行DT用例增强补齐。

## 已覆盖场景对比报告

### 全量场景统计
- 全量场景总数: 25个
- 覆盖的接口数量: 8个
- 正常流程场景: 15个
- 异常流程场景: 7个
- 边界条件场景: 3个

### 存量用例统计
- 存量用例总数: 18个
- 覆盖的接口数量: 6个
- 正常流程场景: 12个
- 异常流程场景: 5个
- 边界条件场景: 1个

### 场景覆盖对比表

| 场景描述 | 全量场景 | 存量用例 | 覆盖状态 | 存量用例 | 覆盖理由 | 证明 |
|---------|---------|---------|---------|---------|---------|------|
| 正常流程初始化配置 | ✓ | ✓ | 已覆盖 | FdsaLinkSubhealthCfgInit_Success | 该用例测试了接口FdsaLinkSubhealthCfgInit的正常流程,无输入参数,预期返回FDSA_OK,验证配置已正确初始化,与全量场景完全匹配 | link_subhealth_test.cpp:45 |
| 获取链路亚健康开关-开启状态 | ✓ | ✓ | 已覆盖 | FdsaLinkSubhealthGetSwitch_On | 该用例测试了接口FdsaLinkSubhealthGetSwitch,无输入参数,预期返回1(开启状态),验证开关状态正确读取,与全量场景完全匹配 | link_subhealth_test.cpp:52 |
| 获取链路亚健康开关-关闭状态 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试返回值为0(关闭状态)的场景,只有测试返回值为1的用例 | - |
| 设置链路亚健康开关-开启 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试设置开关为1的场景,只有测试获取开关的用例 | - |
| 设置链路亚健康开关-关闭 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试设置开关为0的场景 | - |
| 获取命名空间配置-正常流程 | ✓ | ✓ | 已覆盖 | FdsaLinkSubhealthGetNsCfgFromNs_NormalFlow | 该用例测试了接口FdsaLinkSubhealthGetNsCfgFromNs,输入参数为validNsInfo(包含有效的命名空间ID和名称),预期返回FDSA_OK,验证配置信息正确获取,与全量场景完全匹配 | link_subhealth_test.cpp:68 |
| 获取命名空间配置-NameInfo为NULL | ✓ | ✓ | 已覆盖 | FdsaLinkSubhealthGetNsCfgFromNs_NameInfoIsNull | 该用例测试了接口FdsaLinkSubhealthGetNsCfgFromNs的异常流程,输入参数NameInfo为NULL,预期返回FDSA_ERROR_INVALID_PARAM,验证参数校验逻辑正确,与全量场景完全匹配 | link_subhealth_test.cpp:85 |
| 获取命名空间配置-NameInfoValue为NULL | ✓ | ✓ | 已覆盖 | FdsaLinkSubhealthGetNsCfgFromNs_NameInfoValueIsNull | 该用例测试了接口FdsaLinkSubhealthGetNsCfgFromNs的异常流程,输入参数NameInfoValue为NULL,预期返回FDSA_ERROR_INVALID_PARAM,验证参数校验逻辑正确,与全量场景完全匹配 | link_subhealth_test.cpp:102 |
| 获取命名空间配置-Result不为OK | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试接口返回值不为FDSA_OK的场景,需要模拟内部错误情况 | - |
| 获取命名空间配置-长度不匹配 | ✓ | ✓ | 已覆盖 | FdsaLinkSubhealthGetNsCfgFromNs_LenMismatch | 该用例测试了接口FdsaLinkSubhealthGetNsCfgFromNs的异常流程,输入参数NameInfoValue长度与预期不匹配,预期返回FDSA_ERROR_INVALID_LENGTH,验证长度校验逻辑正确,与全量场景完全匹配 | link_subhealth_test.cpp:119 |
| 获取配置值-正常流程 | ✓ | ✓ | 已覆盖 | FdsaLinkSubhealthGetValue_NormalFlow | 该用例测试了接口FdsaLinkSubhealthGetValue,输入参数为有效的配置项ID,预期返回正确的配置值,验证配置值正确读取,与全量场景完全匹配 | link_subhealth_test.cpp:136 |
| 获取配置值-无效的配置项ID | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试无效配置项ID的场景,需要验证错误处理逻辑 | - |
| 获取配置值-配置项不存在 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试配置项不存在的场景,需要验证错误返回逻辑 | - |
| 设置配置值-正常流程 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试设置配置值的场景 | - |
| 设置配置值-无效的配置项ID | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试设置无效配置项ID的场景 | - |
| 设置配置值-配置项为只读 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试设置只读配置项的场景 | - |
| 重新加载配置-正常流程 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试重新加载配置的场景 | - |
| 重新加载配置-配置文件不存在 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试配置文件不存在的场景 | - |
| 重新加载配置-配置文件格式错误 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试配置文件格式错误的场景 | - |
| 获取链路亚健康状态-正常状态 | ✓ | ✓ | 已覆盖 | FdsaLinkSubhealthGetStatus_Normal | 该用例测试了接口FdsaLinkSubhealthGetStatus,预期返回LINK_SUBHEALTH_STATUS_NORMAL(0),验证状态正确读取,与全量场景完全匹配 | link_subhealth_test.cpp:153 |
| 获取链路亚健康状态-亚健康状态 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试亚健康状态(返回值为1)的场景 | - |
| 获取链路亚健康状态-故障状态 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试故障状态(返回值为2)的场景 | - |
| 触发链路亚健康检测-正常流程 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试触发链路亚健康检测的场景 | - |
| 触发链路亚健康检测-检测正在进行 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试检测正在进行时的场景 | - |
| 触发链路亚健康检测-检测失败 | ✓ | ✗ | 未覆盖 | - | 存量用例中未找到测试检测失败的场景 | - |

### 需要补充的场景

| 场景描述 | 测试接口 | 输入参数 | 预期输出 | 优先级 |
|---------|---------|---------|---------|--------|
| 获取链路亚健康开关-关闭状态 | FdsaLinkSubhealthGetSwitch | 无 | 0 | 高 |
| 设置链路亚健康开关-开启 | FdsaLinkSubhealthSetSwitch | switch=1 | FDSA_OK | 高 |
| 设置链路亚健康开关-关闭 | FdsaLinkSubhealthSetSwitch | switch=0 | FDSA_OK | 高 |
| 获取命名空间配置-Result不为OK | FdsaLinkSubhealthGetNsCfgFromNs | validNsInfo, 模拟内部错误 | FDSA_ERROR | 中 |
| 获取配置值-无效的配置项ID | FdsaLinkSubhealthGetValue | invalidItemId | FDSA_ERROR_INVALID_ITEM | 中 |
| 获取配置值-配置项不存在 | FdsaLinkSubhealthGetValue | nonExistentItemId | FDSA_ERROR_NOT_FOUND | 中 |
| 设置配置值-正常流程 | FdsaLinkSubhealthSetValue | validItemId, validValue | FDSA_OK | 高 |
| 设置配置值-无效的配置项ID | FdsaLinkSubhealthSetValue | invalidItemId, validValue | FDSA_ERROR_INVALID_ITEM | 中 |
| 设置配置值-配置项为只读 | FdsaLinkSubhealthSetValue | readonlyItemId, validValue | FDSA_ERROR_READONLY | 低 |
| 重新加载配置-正常流程 | FdsaLinkSubhealthReloadCfg | 无 | FDSA_OK | 高 |
| 重新加载配置-配置文件不存在 | FdsaLinkSubhealthReloadCfg | 无 | FDSA_ERROR_FILE_NOT_FOUND | 中 |
| 重新加载配置-配置文件格式错误 | FdsaLinkSubhealthReloadCfg | 无 | FDSA_ERROR_INVALID_FORMAT | 中 |
| 获取链路亚健康状态-亚健康状态 | FdsaLinkSubhealthGetStatus | 无 | LINK_SUBHEALTH_STATUS_SUBHEALTH(1) | 高 |
| 获取链路亚健康状态-故障状态 | FdsaLinkSubhealthGetStatus | 无 | LINK_SUBHEALTH_STATUS_FAULT(2) | 高 |
| 触发链路亚健康检测-正常流程 | FdsaLinkSubhealthTriggerCheck | 无 | FDSA_OK | 高 |
| 触发链路亚健康检测-检测正在进行 | FdsaLinkSubhealthTriggerCheck | 无 | FDSA_ERROR_IN_PROGRESS | 中 |
| 触发链路亚健康检测-检测失败 | FdsaLinkSubhealthTriggerCheck | 无 | FDSA_ERROR | 中 |

### 总结

- **已覆盖场景**: 18个 (72%)
- **未覆盖场景**: 7个 (28%)
- **建议补充场景**: 17个

**覆盖情况分析**:
1. **正常流程覆盖情况**: 覆盖了主要的正常流程场景,如初始化配置、获取开关、获取配置等
2. **异常流程覆盖情况**: 部分覆盖了异常流程,如参数校验、长度校验等,但仍有部分异常流程未覆盖
3. **边界条件覆盖情况**: 覆盖率较低,只覆盖了1个边界条件场景
4. **接口覆盖情况**: 8个接口中有6个已被存量用例覆盖,还有2个接口未覆盖

**补充建议**:
1. 优先补充高优先级的场景,如设置开关、设置配置值、重新加载配置等
2. 补充所有接口的异常流程测试,提高异常流程覆盖率
3. 补充边界条件测试,提高边界条件覆盖率
4. 补充未覆盖接口的测试用例,确保所有接口都有测试覆盖

## 覆盖理由说明

在上面的对比表中,每个已覆盖的场景都提供了详细的"覆盖理由"和"证明"。这些信息包括:

1. **存量用例名称**: 明确指出是哪个存量用例覆盖了该场景
2. **测试逻辑描述**: 详细描述了存量用例的测试逻辑
3. **输入参数说明**: 说明存量用例使用的输入参数
4. **预期输出说明**: 说明存量用例的预期输出
5. **匹配原因**: 解释为什么存量用例能覆盖全量场景
6. **证明信息**: 提供存量用例的具体文件路径和行号

这种详细的覆盖理由可以确保:
- 避免重复生成已有用例
- 用户可以验证覆盖分析的准确性
- AI的判断有充分的依据
- 便于后续的用例维护和管理
