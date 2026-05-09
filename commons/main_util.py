"""
主执行器 - 编排测试用例执行流程
"""

import sys
from typing import Any, Dict, Optional

from commons.assert_util import ResponseValidator
from commons.extract_util import extract_engine
from commons.logger import logger
from commons.request_util import request_engine
from commons.settings import config


def execute_test_case(case_obj) -> Dict[str, Any]:
    """执行单个测试用例

    流程:
    1. 提取用例元信息 (feature/story/title)
    2. 发送 HTTP 请求
    3. 提取响应数据（如需）
    4. 校验响应（如需）

    Args:
        case_obj: TestCaseObj 对象

    Returns:
        执行结果字典 {title, status}
    """
    case_title = getattr(case_obj, "title", "未命名用例")
    request_info = getattr(case_obj, "request", {})
    extract_info = getattr(case_obj, "extract", {})
    validate_info = getattr(case_obj, "validate", {})

    logger.info(f"▶️  执行用例: {case_title}")

    try:
        # 校验请求信息
        if not request_info:
            raise ValueError("request 信息为空")

        method = request_info.get("method", "get")
        url = request_info.get("url", "")

        # 构造请求参数（排除 method/url）
        req_kwargs = {k: v for k, v in request_info.items() if k not in ("method", "url")}

        # 发送请求
        response = request_engine.send(method, url, **req_kwargs)
        if response is None:
            raise RuntimeError("请求返回为空")

        # 提取响应数据
        if extract_info:
            extract_engine.extract_response_info(response, extract_info)

        # 校验响应
        if validate_info:
            validator = ResponseValidator(response)
            validator.validate(validate_info)

        logger.info(f"✅ 用例执行成功: {case_title}")
        return {"title": case_title, "status": "passed"}

    except AssertionError as e:
        logger.error(f"❌ 断言失败 [{case_title}]: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ 用例执行异常 [{case_title}]: {e}", exc_info=True)
        raise


def run_smoke():
    """运行冒烟测试 - 预留入口"""
    logger.info("运行冒烟测试...")
    # TODO: 支持 -m smoke 标记
    pass


def cleanup():
    """测试后清理"""
    request_engine.close()
    logger.info("测试资源已释放")
