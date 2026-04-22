import json

from cerberus import Validator  # 校验结构化数据（如 YAML 解析后的字典）是否符合规则
from commons.logger import logger

schema = {
    # Allure报告核心字段（必填）
    "feature": {"type": "string", "required": True, "empty": False},
    "story": {"type": "string", "required": True, "empty": False},
    "title": {"type": "string", "required": True, "empty": False},

    # 请求信息（必填字典）
    "request": {
        "type": "dict",
        "required": True,
        "schema": {
            "method": {"type": "string", "required": True, "allowed": ["get", "post", "put", "delete"]},  # 限制请求方法
            "url": {"type": "string", "required": True, "empty": False},
            "headers": {"type": "dict", "required": False},
            "params": {"type": "dict", "required": False},
            "json": {"type": "dict", "required": False},
            "data": {"type": "dict", "required": False},
            "files": {"type": "string", "required": False, "empty": False},
        }
    },

    # 提取参数（可选字典，key为提取名，value为JSONPath表达式）
    "extract": {
        "type": "dict",
        "required": False,
        "valueschema": {"type": "list", "empty": False}  # 限制extract的值为非空字符串
    },

    # 校验项
    "validate": {
        "type": "dict",
        "required": False,
        "valuesrules": {"type": "list", "required": False}
    }
}


class TestCaseObj:
    """用例结构化对象，封装feature/story/title等属性"""

    def __init__(self, feature, story, title, **kwargs):
        self.feature = feature
        self.story = story
        self.title = title
        self.request = kwargs.get("request")
        self.params = kwargs.get("params")
        self.json = kwargs.get("json")
        self.data = kwargs.get("data")
        self.files = kwargs.get("files")
        self.validate = kwargs.get("validate")
        self.extract = kwargs.get("extract")
        # 可补充其他字段，如self.request = kwargs.get("request")


def validate_case_data(case_data):
    """校验case_data是否合法"""
    v = Validator(schema)
    if not v.validate(case_data):
        return False, _format_cerberus_errors(v.errors)
    return True, None


def _format_cerberus_errors(errors):
    """
    将 Cerberus 的错误字典转换为易读字符串，降低沟通成本

    支持处理：
    - 平铺字段错误：{'field': ['error1', 'error2']}
    - 嵌套字段错误：{'request': [{'method': ['unallowed value']}]}
    """
    msgs = []
    for field, err_list in errors.items():
        # 递归处理嵌套错误
        formatted_errors = []
        for item in err_list:
            if isinstance(item, str):
                # 简单字符串错误
                formatted_errors.append(item)
            elif isinstance(item, dict):
                # 嵌套字典错误（如子字段校验失败）
                for sub_field, sub_errors in item.items():
                    if isinstance(sub_errors, list):
                        formatted_errors.append(f"{sub_field}: {', '.join(sub_errors)}")
                    else:
                        formatted_errors.append(f"{sub_field}: {sub_errors}")
            else:
                # 兜底：其他类型转为字符串
                formatted_errors.append(str(item))

        # 拼接错误信息
        error_detail = '; '.join(formatted_errors) if formatted_errors else '(无详细信息)'
        msgs.append(f"  - 字段 '{field}': {error_detail}")

    return "\n".join(msgs)


def build_test_case_obj(case_data):
    """根据校验后的数据构建TestCaseObj对象"""
    return TestCaseObj(
        feature=case_data.get("feature"),
        story=case_data.get("story"),
        title=case_data.get("title"),
        request=case_data.get("request"),
        params=case_data.get("params"),
        json=case_data.get("json"),
        data=case_data.get("data"),
        files=case_data.get("files"),
        extract=case_data.get("extract"),
        validate=case_data.get("validate"),
    )


def verify_yaml(case_data, yaml_filename):
    """
    校验 YAML 并构建完整的 TestCaseObj 对象。
    """
    try:
        # 1. 执行校验
        is_valid, errors = validate_case_data(case_data)
        if not is_valid:
            logger.error(f"YAML 校验失败 [{yaml_filename}]:\n{errors}")
            return False, errors

        # 2. 构建完整对象
        obj = build_test_case_obj(case_data)
        logger.info(f"YAML [{yaml_filename}] 加载成功 | Feature: {obj.feature} | Title: {obj.title}")
        return obj

    except Exception as e:
        # 增加堆栈跟踪，便于定位框架代码 Bug
        logger.error(f"框架内部异常 [{yaml_filename}]: {e}", exc_info=True)
        return False, f"框架异常: {str(e)}"
