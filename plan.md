# 零代码接口自动化框架 - 项目需求与技术实现方案

## 一、项目概述

### 1.1 目标
实现一个基于 **Python + Requests + Pytest + Allure + Jenkins** 的零代码接口自动化测试框架。
测试人员只需维护 YAML 格式的测试场景文件，即可实现：
- HTTP 接口请求（GET/POST/文件上传）
- 接口间数据传递（提取响应字段供后续用例使用）
- 参数化数据驱动（YAML内联参数 / CSV文件）
- 动态参数生成（热加载函数）
- 灵活的断言机制（精确匹配 / 模糊包含）
- 美观的 Allure 测试报告
- Jenkins CI/CD 流水线集成

### 1.2 技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.9+ | 框架开发语言 |
| requests | 2.31+ | HTTP 请求客户端 |
| pytest | 7.0+ | 测试执行引擎 |
| allure-pytest | 2.13+ | 测试报告生成 |
| PyYAML | 6.0+ | YAML 测试用例解析 |
| jsonpath-ng | 1.6+ | JSON 路径提取 |
| python-dotenv | 1.0+ | 环境变量加载 |
| jmespath | 1.0+ | JSON 数据查询 |
| loguru | 0.7+ | 日志管理 |

### 1.3 项目目录结构
```
InterfaceDemo/
├── commons/                  # 框架核心模块
│   ├── __init__.py
│   ├── assert_util.py        # 断言引擎
│   ├── case_util.py          # 用例发现与加载
│   ├── db_util.py            # 数据库工具（预留）
│   ├── ddt_util.py           # 数据驱动引擎
│   ├── extract_util.py       # 响应提取引擎
│   ├── logger.py             # 日志模块
│   ├── main_util.py          # 主入口/测试执行器
│   ├── model_util.py         # YAML 数据模型解析
│   ├── request_util.py       # HTTP 请求引擎
│   ├── settings.py           # 全局配置单例
│   └── yaml_util.py          # YAML 文件读写
├── configs/                  # 配置文件
│   ├── config.yaml           # 多环境配置
│   └── setting.py            # 配置加载器
├── testcases/                # 测试用例目录
│   ├── conftest.py           # pytest fixtures
│   └── <module>/             # 按模块划分子目录
│       └── *.yaml            # YAML 测试用例
├── data/                     # CSV 数据文件目录
├── logs/                     # 日志输出目录
├── reports/                  # 测试报告目录
│   ├── allure-results/       # Allure 原始结果
│   └── allure-report/        # Allure HTML 报告
├── temps/                    # 临时文件目录
├── run.py                    # 运行入口脚本
├── debug_talk.py             # 热加载函数库
├── extract.yaml              # 接口变量持久化存储
├── run.env                   # 环境变量文件
├── requirements.txt          # 项目依赖
├── pytest.ini                # pytest 配置
├── 框架规范.txt              # 框架使用规范
└── CLAUDE.md                 # 代码生成规范
```

---

## 二、核心模块设计

### 2.1 YAML 测试用例模型

#### 一级关键字结构
```yaml
-
  name: 用例名称（可选，从 title 推导）
  feature: Allure - 功能模块
  story: Allure - 子功能/接口
  title: 用例标题
  request:                    # 必需
    method: get/post/put/delete/patch
    url: ${env(base_url)}/api/xxx
    headers:                  # 可选
      Content-Type: application/json
    params:                   # GET 参数（可选）
      key: value
    json:                     # POST JSON 体（可选）
      key: value
    data:                     # POST 表单（可选）
      key: value
    files:                    # 文件上传（可选）
      field_name: "/path/to/file"
    cookies:                  # Cookie（可选）
      key: value
    timeout: 30               # 超时秒数（可选，默认30）
  extract:                    # 响应提取（可选）
    var_name: [json, "$.data.token", 0]
    var_name2: [text, '"key":"(.*?)"', 1]
  validate:                   # 断言（必需）
    equals:
      描述: [期望值, 实际来源]
    contains:
      描述: [期望子串, 实际来源]
  parametrize:                # 数据驱动（可选）
    - ["param1", "param2"]    # 第一行是变量名
    - ["val1", "val2"]        # 后续行是测试数据
    - ["val3", "val4"]
```

#### 变量引用语法
| 语法 | 说明 | 示例 |
|------|------|------|
| `${env(KEY)}` | 引用环境变量 | `${env(base_url)}` |
| `${func(arg)}` | 调用热加载函数 | `${random_phone()}` |
| `$ddt{field}` | 数据驱动参数化 | `$ddt{username}` |
| `${read_yaml(key)}` | 读取 extract.yaml | `${read_yaml(access_token)}` |

### 2.2 模块职责

#### commons/settings.py - 全局配置
- 单例模式，管理全局配置项
- 包含：base_url、headers、timeout、日志级别、extract.yaml 路径等
- 初始化时加载 run.env 和 configs/config.yaml

#### commons/logger.py - 日志模块
- 基于 loguru 封装统一日志
- 支持控制台 + 文件双输出
- 日志按天切割，保留 7 天

#### commons/yaml_util.py - YAML 读写
- 读取 YAML 测试用例文件
- 读写 extract.yaml（接口变量持久化）
- 处理 YAML 解析异常

#### commons/model_util.py - 数据模型
- 将 YAML 字典结构转换为 Python 数据类/NamedTuple
- 校验必填字段（request.method, request.url）
- 提供类型安全的字段访问

#### commons/request_util.py - HTTP 请求引擎
- 封装 requests.Session，自动管理 Cookie
- 支持 GET/POST/PUT/DELETE/PATCH/文件上传
- 自动解析 `${env()}`, `${func()}`, `$ddt{}` 变量占位符
- 统一处理超时、重试、异常
- 返回标准化响应对象（包含 status_code, headers, json, text）

#### commons/extract_util.py - 响应提取引擎
- JSONPath 提取：`[json, "$.data.token", 0]`
- 正则提取：`[text, '"token":"(.*?)"', 1]`
- 提取结果写入 extract.yaml 和内存变量池

#### commons/assert_util.py - 断言引擎
- equals 断言：精确匹配（支持 status_code, json, text, headers）
- contains 断言：子串/子列表包含
- 断言失败抛出 AssertionError（pytest 可捕获）
- 断言结果记录到日志和 Allure 附件

#### commons/ddt_util.py - 数据驱动引擎
- 解析 YAML 内 parametrize 列表
- 读取 CSV 文件进行数据驱动
- 生成 pytest 参数化测试用例

#### commons/case_util.py - 用例发现与加载
- 扫描 testcases/ 目录下所有 .yaml 文件
- 按模块加载用例
- 生成 pytest 测试函数（动态注册）

#### commons/main_util.py - 主执行器
- 命令行入口（argparse）
- 初始化框架环境（日志、配置、变量池）
- 发现并执行测试用例
- 生成 Allure 报告

#### configs/setting.py - 配置加载
- 加载 configs/config.yaml
- 支持环境切换（default/dev/prod）
- 合并 run.env 环境变量

#### debug_talk.py - 热加载函数库
- 用户自定义的动态参数生成函数
- 框架通过反射调用这些函数
- 示例函数：随机手机号、时间戳、UUID、随机字符串等

---

## 三、执行流程

```
1. 用户执行: python run.py 或 pytest
2. main_util.py 初始化:
   a. 加载 run.env 环境变量
   b. 加载 configs/config.yaml 配置
   c. 初始化日志
   d. 清空 extract.yaml
3. case_util.py 发现测试用例:
   a. 扫描 testcases/**/*.yaml
   b. 解析每个 YAML 文件为用例列表
4. 对每个 YAML 用例:
   a. model_util.py 解析为数据模型
   b. 如有 parametrize，由 ddt_util.py 展开为多组数据
   c. request_util.py 构建并发送 HTTP 请求
      - 变量替换: ${env()}, ${func()}, $ddt{}
   d. 如有 extract，由 extract_util.py 提取响应数据
   e. 如有 validate，由 assert_util.py 执行断言
5. pytest 收集结果，allure-pytest 生成报告数据
6. 生成 Allure HTML 报告
```

---

## 四、待完成工作清单

### Phase 1: 核心引擎（已完成度评估）
| 模块 | 文件 | 完成度 | 说明 |
|------|------|--------|------|
| 日志 | commons/logger.py | 80% | 需补充按天切割逻辑 |
| 配置 | configs/setting.py | 70% | 需补充多环境切换 |
| 配置 | commons/settings.py | 70% | 需补全单例和变量池 |
| YAML读写 | commons/yaml_util.py | 80% | 需补充异常处理 |
| 请求引擎 | commons/request_util.py | 40% | 核心功能需完善 |
| 数据模型 | commons/model_util.py | 60% | 需补全字段校验 |
| 断言引擎 | commons/assert_util.py | 50% | 需实现 equals/contains |
| 提取引擎 | commons/extract_util.py | 50% | 需实现 jsonpath/regex |
| 数据驱动 | commons/ddt_util.py | 40% | 需实现 CSV/parametrize |
| 用例加载 | commons/case_util.py | 30% | 需实现动态测试注册 |
| 主执行器 | commons/main_util.py | 40% | 需补全流程 |
| 热加载 | debug_talk.py | 50% | 需补充常用函数 |
| 运行入口 | run.py | 60% | 需完善参数解析 |
| pytest集成 | testcases/conftest.py | 50% | 需补全 fixtures |

### Phase 2: 报告与集成
- [ ] 完善 Allure 报告注解（feature/story/step/attachment）
- [ ] 编写 Jenkinsfile pipeline 脚本
- [ ] 配置 pytest.ini 的 allure 参数

### Phase 3: 辅助功能
- [ ] 补充常用热加载函数到 debug_talk.py
- [ ] CSV 数据文件目录和读取
- [ ] 数据库工具（预留，按需开发）
- [ ] 并发执行支持（pytest-xdist）

---

## 五、关键技术决策

### 5.1 变量替换策略
- **时机**: 在发送请求前，对 request 中的所有字符串值进行递归变量替换
- **优先级**: $ddt{} > ${env()} > ${read_yaml()} > ${func()}
- **实现**: 递归遍历 request 字典，对每个字符串值调用变量解析器

### 5.2 接口关联实现
- 提取结果存储在两个位置：
  1. extract.yaml 文件（跨 YAML 文件的变量共享）
  2. 内存变量池（同一 YAML 文件内用例间的变量共享）
- 通过 `${read_yaml(key)}` 语法读取

### 5.3 数据驱动实现
- YAML 内联 parametrize：直接展开为 pytest.mark.parametrize
- CSV 文件：读取后转为参数列表，同样通过 pytest.mark.parametrize 注入
- 使用 pytest 的 parametrize_ids + parametrize_values 机制

### 5.4 动态测试注册
- 不使用传统的 test_*.py 文件编写测试函数
- 由 case_util.py 扫描 YAML 后，通过 pytest_generate_tests 钩子动态生成测试函数
- 每个 YAML 用例对应一个 pytest 测试用例，parametrize 数据展开为多个测试实例

### 5.5 断言设计
- equals/contains 的实际来源支持：
  - `status_code` - 响应状态码
  - `json` - 整个 JSON 响应
  - `jsonpath` - JSONPath 查询结果
  - `text` - 响应文本
  - `headers` - 响应头
- 断言失败时记录详细的期望值 vs 实际值到日志和 Allure
