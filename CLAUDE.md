# CLAUDE.md - 代码生成规范

本文件定义了 InterfaceDemo 零代码接口自动化框架的代码生成规范。在编写或修改 Python 代码时，必须遵循以下规范。

## 技术栈

- **Python 3.9+**
- **requests** - HTTP 请求
- **pytest** - 测试执行
- **allure-pytest** - 测试报告
- **loguru** - 日志管理
- **PyYAML** - YAML 解析
- **jsonpath-ng** - JSON 路径提取

## 编码规范

### 命名
- 模块/文件: `snake_case.py`（如 `request_util.py`）
- 类: `PascalCase`（如 `RequestEngine`）
- 函数/变量: `snake_case`（如 `send_request`）
- 常量: `UPPER_SNAKE_CASE`（如 `DEFAULT_TIMEOUT`）
- 私有方法/属性: 前缀 `_`（如 `_parse_url`）

### 类型注解
- 所有函数必须标注参数类型和返回值类型
- 使用 `typing` 模块的 `Optional`, `List`, `Dict`, `Any`, `Union` 等
- 示例:
  ```python
  def send_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
  ```

### 文档字符串
- 公共模块/类/函数必须有 docstring
- 使用 Google 风格 docstring
- 私有函数 docstring 可省略
- 示例:
  ```python
  def send_request(method: str, url: str) -> Dict[str, Any]:
      """发送 HTTP 请求并返回标准化响应。

      Args:
          method: HTTP 方法 (get/post/put/delete/patch)
          url: 请求地址，支持 ${env()} 等变量替换

      Returns:
          包含 status_code, headers, json, text 的字典
      """
  ```

### 异常处理
- 使用自定义异常类，不要直接 raise Exception
- 所有框架异常定义在对应模块中或统一放在 `commons/exceptions.py`
- 异常必须携带清晰的错误信息
- 示例:
  ```python
  class RequestError(Exception):
      """HTTP 请求异常"""
      pass

  raise RequestError(f"请求失败: {url}, 原因: {e}")
  ```

### 日志
- 使用 `loguru.logger` 进行日志输出
- 日志级别选择:
  - `logger.debug()` - 调试信息（请求详情、变量值）
  - `logger.info()` - 关键流程节点（用例开始/结束）
  - `logger.warning()` - 非致命警告
  - `logger.error()` - 错误信息
- 所有异常必须记录日志后抛出

### 文件组织
- 每个 `.py` 文件职责单一，不做多功能聚合
- `commons/` 下每个文件对应一个框架子模块
- 导入顺序: 标准库 → 第三方库 → 本地模块，各组空一行

### 配置管理
- 配置项通过 `commons/settings.py` 单例获取
- 不要硬编码路径、URL、超时等配置值
- 环境变量通过 `${env(KEY)}` 或 `os.getenv()` 获取

## 框架模块约定

### commons/settings.py
- 全局唯一配置单例
- 职责: 加载 run.env + configs/config.yaml，提供配置访问
- 提供 `get(key, default)` 和 `set(key, value)` 方法
- 维护内存变量池（接口间传递变量）

### commons/logger.py
- 封装 loguru 配置
- 初始化时配置控制台 + 文件输出
- 日志文件按天切割，保留 7 天

### commons/yaml_util.py
- `read_yaml(path)` - 读取 YAML 文件返回 Python 对象
- `write_yaml(path, data)` - 写入数据到 YAML 文件
- `read_extract_yaml()` - 读取 extract.yaml
- `write_extract_yaml(data)` - 追加数据到 extract.yaml

### commons/model_util.py
- `TestCase` 数据类: 包含 feature, story, title, request, extract, validate, parametrize 字段
- `parse_test_case(yaml_data) -> TestCase` - 解析 YAML 数据为 TestCase
- 校验必填字段缺失时抛出 `ValidationError`

### commons/request_util.py
- `RequestEngine` 类: 封装 requests.Session
- `send(method, url, **kwargs) -> Dict[str, Any]` - 发送请求
- `replace_variables(data) -> Any` - 递归替换变量占位符
- 支持: `${env(KEY)}`, `${func(args)}`, `$ddt{field}`, `${read_yaml(key)}`

### commons/extract_util.py
- `extract_by_json(response_text, jsonpath_expr, index) -> Any` - JSONPath 提取
- `extract_by_regex(response_text, pattern, group_index) -> Any` - 正则提取
- `save_extracted_data(key, value)` - 保存提取结果到 extract.yaml 和内存

### commons/assert_util.py
- `assert_equals(actual, expected, description="")` - 精确匹配断言
- `assert_contains(substring, actual, description="")` - 包含断言
- 断言失败时抛出 `AssertionError`，消息包含描述、期望值、实际值

### commons/ddt_util.py
- `load_csv(csv_path) -> List[Dict]` - 读取 CSV 文件
- `expand_parametrize(parametrize_data) -> Tuple[List[str], List[Any]]` - 展开参数化数据

### commons/case_util.py
- `discover_testcases(root_dir="testcases/") -> List[str]` - 发现所有 YAML 用例文件
- `load_yaml_testcases(yaml_path) -> List[TestCase]` - 加载单个 YAML 文件中的用例

### commons/main_util.py
- `run(args)` - 主执行入口
- 初始化环境 → 发现用例 → 执行测试 → 生成报告

### debug_talk.py
- 热加载函数定义文件，用户可扩展
- 函数为普通函数，不需要 self 参数
- 框架通过函数名反射调用

## 测试用例 YAML 规范

```yaml
-
  feature: 模块名称
  story: 接口名称
  title: 用例标题
  request:
    method: get
    url: ${env(base_url)}/api/path
    params:
      key: value
  extract:
    var_name: [json, "$.data.field", 0]
  validate:
    equals:
      断言描述: [期望值, 实际来源]
    contains:
      断言描述: [期望子串, 实际来源]
  parametrize:
    - ["var1", "var2"]
    - ["val1", "val2"]
```

## 提交规范

- commit message 格式: `type: description`
- type: `feat` / `fix` / `refactor` / `docs` / `chore` / `test`
