# FDSA项目DT测试参考信息

本文档提供了FDSA项目中DT测试相关的参考信息,帮助生成高质量的DT用例。

## 项目概述

FDSA (故障诊断与自动修复系统) 是华为存储系统的核心组件,提供故障检测、诊断和自动修复功能。

### 产品线

- **Fusion** (分布式FDSA): 面向分布式存储场景
- **Dorado** (闪存FDSA): 面向全闪存存储场景

## 目录结构

### Fusion产品线

```
fusion/
├── product/taishan_src/fdsa/    # FDSA核心代码
│   ├── src/                     # 源码
│   │   ├── agent/              # 客户端代理
│   │   ├── core/               # 核心引擎
│   │   ├── monitor/            # 监控模块
│   │   └── plugins/            # 插件实现
│   ├── include/                # 头文件
│   └── publish/                # 发布文件
├── product/test/fdsa/fdsa_dt_linux/  # DT测试目录
│   ├── dt_src/                 # 测试源码
│   ├── 0_build_llt_framework.sh
│   ├── 1_test_framework.sh
│   ├── 2_build_llt_bin.sh
│   ├── 3_run.sh
│   └── 4_build_coverage_report_for_html.sh
└── build.py                    # Python构建脚本
```

### Dorado产品线

```
dorado/
├── Product/taishan_src/ctrl/fdsa/  # FDSA控制面代码
├── Product/test/fdsa_dt_linux/     # DT测试目录
│   ├── fdsa_llt_run_all.sh
│   ├── fdsa_llt_run_module.sh
│   └── fdsa_llt_run_prepare.sh
└── build.py                        # Python构建脚本
```

## DT测试框架

### 测试框架技术栈

- **测试框架**: GTEST (Google Test)
- **打桩框架**: MOCKCPP
- **覆盖率工具**: GCOV/LCOV
- **构建工具**: Bazel/Make

### DT测试目录结构

#### Fusion DT目录

```
fusion/product/test/fdsa/fdsa_dt_linux/
├── dt_src/                    # 测试源码目录
│   ├── Makefile_fdsacore     # 主Makefile
│   └── <模块名>/             # 各模块测试
├── lib/                       # 测试库
├── bin/                       # 测试可执行文件
├── coverage/                  # 覆盖率报告
└── scripts/                   # 辅助脚本
```

#### Dorado DT目录

```
dorado/Product/test/fdsa_dt_linux/
├── dt_src/                    # 测试源码目录
├── lib/                       # 测试库
├── bin/                       # 测试可执行文件
└── scripts/                   # 辅助脚本
```

## 常用命令

### Fusion DT测试

```bash
cd fusion/product/test/fdsa/fdsa_dt_linux

# 1. 构建测试框架
./0_build_llt_framework.sh

# 2. 测试框架
./1_test_framework.sh

# 3. 构建测试二进制
./2_build_llt_bin.sh

# 4. 运行测试
./3_run.sh

# 5. 生成HTML覆盖率报告
./4_build_coverage_report_for_html.sh

# 生成GCOV覆盖率报告
./4_build_coverage_report_for_gcov.sh

# 清理测试框架
./9_clean_framework.sh
```

### Dorado DT测试

```bash
cd dorado/Product/test/fdsa_dt_linux

# 构建并运行所有测试
./fdsa_llt_run_all.sh

# 构建并运行指定模块测试
./fdsa_llt_run_module.sh <module_name>

# 准备测试环境
./fdsa_llt_run_prepare.sh
```

## 核心模块

### 共享模块结构

- **agent/**: FDSA客户端代理,负责与服务器通信
- **common/**: 公共模块,包含集群管理、通信、命名服务等
- **core/**: 核心引擎
  - cache/: 缓存管理
  - conf/: 配置管理
  - control/: 流程控制
  - healthcheck/: 健康检查
  - main/: 主程序入口
  - processengine/: 流程引擎
  - selfmonitor/: 自监控
  - statusmanager/: 状态管理
- **daemon/**: 守护进程,负责系统级服务
- **monitor/**: 监控模块
  - base/: 监控基础框架
  - cfgtool_server/: 配置工具服务器
  - diagnose/: 诊断功能
  - recover/: 恢复功能
  - self_monitor/: 自监控
- **plugins/**: 插件系统
- **tool/**: 工具集
- **util/**: 工具库

### Fusion特有插件

- `clientlite/`: 轻量级客户端
- `fault_repair/`: 故障修复 (包含 client, master, agent)
- `isolation/`: 隔离插件
- `libiocheck/`: IO检查
- `libproc_link_info_collect/`: 进程链路信息收集
- `libsmartdiagnose/`: 智能诊断
- `link_subhealth/`: 链路亚健康

### Dorado特有插件

- `libapposdwrapper/`: 应用OSD包装器
- `libcorefaultcheck/`: 核心故障检查
- `libioabnormal/`: IO异常
- `libkillprocess/`: 进程杀掉
- `libprocessfault/`: 进程故障
- `libsmartdiagnose/`: 智能诊断
- `libtaskmanager/`: 任务管理器

## MOCKCPP打桩示例

### 基础打桩

```cpp
#include "mockcpp/mockcpp.h"

// 固定返回值打桩
MOCKER(FDSA_CommSendAckMsg).stubs().will(returnValue(FDSA_OK));

// 调用自定义桩函数
MOCKER(FDSA_CommSendAckMsg).stubs().will(invoke(FDSA_CommSendAckMsgStub));

// 基于参数返回不同值
MOCKER(FDSA_GetStatus).stubs()
    .with(eq(1))
    .will(returnValue(FDSA_OK));
MOCKER(FDSA_GetStatus).stubs()
    .with(eq(2))
    .will(returnValue(FDSA_ERROR));
```

### 资源管理打桩

```cpp
// 内存申请打桩
MOCKER(fdsa_malloc).stubs().will(returnValue((void*)0x12345678));

// 内存释放打桩
MOCKER(fdsa_free).stubs().will(returnValue(FDSA_OK));

// 全局变量初始化打桩
MOCKER(FDSA_InitGlobalVar).stubs().will(returnValue(FDSA_OK));
```

### 异步接口打桩

```cpp
// 线程池同步化
MOCKER(ThreadPool_AddTask).stubs().will(invoke(ThreadPool_AddTask_Sync));

// 消息队列同步化
MOCKER(MsgQueue_Send).stubs().will(returnValue(FDSA_OK));

// 事件通知同步化
MOCKER(Event_Notify).stubs().will(returnValue(FDSA_OK));
```

## GTEST测试用例结构

### 三段式结构

```cpp
TEST_F(ClassName, TestName) {
    // Arrange - 准备阶段
    // 初始化测试数据
    // 设置桩函数

    // Act - 执行阶段
    // 调用被测函数

    // Assert - 验证阶段
    // 验证结果
    // 检查桩函数调用
}
```

### 完整示例

```cpp
#include <gtest/gtest.h>
#include "mockcpp/mockcpp.h"
#include "fdsa_common_header.h"

class FDSAProcLinkTest : public ::testing::Test {
protected:
    virtual void SetUp() {
        // 测试前置处理
        MockObjectRepository::instance().registerMockObject("mock_obj");
    }

    virtual void TearDown() {
        // 测试后置处理
        MockObjectRepository::instance().verify();
    }
};

TEST_F(FDSAProcLinkTest, NormalFlow) {
    // Arrange
    uint32_t pid = 1234;
    ProcLinkInfo expected_info;
    expected_info.pid = pid;
    expected_info.status = PROC_LINK_STATUS_ACTIVE;

    MOCKER(FDSA_GetProcLinkInfo).stubs()
        .with(eq(pid))
        .will(returnValue(&expected_info));

    // Act
    ProcLinkInfo* actual_info = FDSA_GetProcLinkInfo(pid);

    // Assert
    ASSERT_NE(actual_info, nullptr);
    EXPECT_EQ(actual_info->pid, expected_info.pid);
    EXPECT_EQ(actual_info->status, expected_info.status);
}

TEST_F(FDSAProcLinkTest, InvalidPid) {
    // Arrange
    uint32_t invalid_pid = 0;

    MOCKER(FDSA_GetProcLinkInfo).stubs()
        .with(eq(invalid_pid))
        .will(returnValue((ProcLinkInfo*)nullptr));

    // Act
    ProcLinkInfo* actual_info = FDSA_GetProcLinkInfo(invalid_pid);

    // Assert
    EXPECT_EQ(actual_info, nullptr);
}
```

## 常见测试场景

### 正常流程测试

```cpp
TEST_F(ClassName, NormalFlow) {
    // 测试正常业务流程
}
```

### 异常流程测试

```cpp
TEST_F(ClassName, InvalidInput) {
    // 测试无效输入
}

TEST_F(ClassName, ResourceNotAvailable) {
    // 测试资源不可用
}
```

### 边界条件测试

```cpp
TEST_F(ClassName, BoundaryMin) {
    // 测试最小边界值
}

TEST_F(ClassName, BoundaryMax) {
    // 测试最大边界值
}
```

### 错误处理测试

```cpp
TEST_F(ClassName, ErrorHandling) {
    // 测试错误处理逻辑
}
```

## 数据库初始化

测试和产品运行需要初始化数据库:

```bash
# Fusion
sqlite3 ${FDSA_BASE}/publish/arr/conf/linux/data/fdsa_global.db < ${FDSA_BASE}/publish/arr/conf/linux/data/fdsa_db.sql
sqlite3 ${FDSA_BASE}/publish/arr/conf/linux/data/fdsa_local.db < ${FDSA_BASE}/publish/arr/conf/linux/data/fdsa_db.sql

# Dorado
sqlite3 ${DORADO_BASE}/Product/publish/arr/conf/linux/data/fdsa_global.db < ${DORADO_BASE}/Product/publish/arr/conf/linux/data/fdsa_db.sql
sqlite3 ${DORADO_BASE}/Product/publish/arr/conf/linux/data/fdsa_local.db < ${DORADO_BASE}/Product/publish/arr/conf/linux/data/fdsa_db.sql
```

## 构建系统

### CMake构建

```bash
# DEBUG构建 (x86_64)
cmake -B build -DCMAKE_BUILD_TYPE=DEBUG -DCPU_TYPE=x86_64
cmake --build build

# RELEASE构建 (ARM)
cmake -B build -DCMAKE_BUILD_TYPE=RELEASE -DCPU_TYPE=arm_64
cmake --build build
```

### Bazel构建

```bash
cd fusion

# Release构建
./mk_fdsa.sh release

# ASAN构建 (地址消毒)
./mk_fdsa.sh asan

# TSAN构建 (线程消毒)
./mk_fdsa.sh tsan

# Debug构建 (默认)
./mk_fdsa.sh debug
```

### SDK构建

```bash
# DEBUG构建
CI/build/script/sdk_build.sh

# RELEASE构建
CI/build/script/sdk_build.sh -b RELEASE

# 清理编译环境
CI/build/script/sdk_build.sh -c
```

## 测试库构建注意事项

在构建测试二进制时,被测库需要去除main符号以避免链接冲突:

```bash
target="fdsa_util fdsa_restricttask localagent _common_plugin ..."
for str in ${target}
do
    ar -x lib${str}.a
    ls *.o | xargs -i objcopy -N main {} {}_new
    ar cqs lib${str}.a *_new
done
```

当新增被测库时,需要:
1. 在Bazel的target中添加该库
2. 在`2_build_llt_bin.sh`的target列表中添加该库名称

## 常见问题

### 编译问题

1. **链接错误**: 检查Makefile中是否正确添加了依赖库
2. **头文件找不到**: 检查include路径是否正确
3. **符号冲突**: 检查是否正确去除了main符号

### 运行问题

1. **CoreDump**: 检查指针是否正确初始化,数组是否越界
2. **测试超时**: 检查是否有死锁或无限循环
3. **内存泄漏**: 使用ASAN或Valgrind检测

### 打桩问题

1. **桩函数不生效**: 检查桩函数名称是否正确
2. **打桩粒度过大**: 减少打桩范围,只打必要的接口
3. **桩函数返回值错误**: 检查返回值类型是否匹配

## 覆盖率分析

### 生成覆盖率报告

```bash
cd fusion/product/test/fdsa/fdsa_dt_linux

# HTML格式
./4_build_coverage_report_for_html.sh

# GCOV格式
./4_build_coverage_report_for_gcov.sh
```

### 覆盖率目标

- **语句覆盖率**: > 80%
- **分支覆盖率**: > 70%
- **函数覆盖率**: > 90%

## 最佳实践

1. **一次只让AI干一件具体的事情**: 先让AI把编译调过,然后用例以测试套为粒度进行调试
2. **人工定位问题**: 当AI自己无法完成任务时,人工定位,并把原因告诉AI
3. **CoreDump问题**: 先人工找到堆栈,然后把堆栈给AI
4. **不要修改业务代码**: DT用例应该只测试,不应该修改被测代码
5. **打桩要合理**: 避免过度打桩导致测试失去意义
6. **检查点要明确**: 每个用例应该有清晰的验证点
7. **用例要可维护**: 避免过于复杂的测试逻辑

## 相关文档

- `CI/build/frame/README.md`: AA构建框架详细说明
- `common/docs/`: 设计文档
- `fusion/README.md`: Fusion产品说明
- `dorado/README.txt`: Dorado产品说明
