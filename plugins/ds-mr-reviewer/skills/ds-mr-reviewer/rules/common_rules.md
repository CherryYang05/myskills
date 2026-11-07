# 通用检视规则

所有MR检视时必须遵守的规则。

### COM-001: 性能优化类修改必须验证数据一致性
- **检查锚点**: MR标题/描述包含"性能优化", 或MR修改意图包含性能优化, 必须验证数据一致性（数量和内容都要验证完全一致）
- **反例**: MR做了性能优化的重构，仅验证了功能正常，数据量一致
- **正例**: 把修改前后的数据导出，使用脚本或工具校验前后数据完全一致

### COM-002: 进行除法或模运算前必须判断除数是否为零
- **检查锚点**: 集合.size()作为除数, / 除法运算, % 模运算, actNes.size(), list.size(), array.length
- **反例**: `(double) i / actNes.size() * LatencyExportTargetMap.PRECESS_FINISH`
- **正例**: `actNes.isEmpty() ? 0 : (double) i / actNes.size() * LatencyExportTargetMap.PRECESS_FINISH`