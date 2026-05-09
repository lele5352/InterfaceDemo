"""
pytest fixtures 配置 - 测试前后置处理

注意：此文件中的日志变量使用 fw_logger 而非 logger，
避免与 pytest 内部的 logger fixture 命名冲突。
"""

import pytest

from commons.logger import logger as fw_logger
from commons.settings import config
from commons.yaml_util import clear_extract_yaml


@pytest.fixture(scope="function", autouse=False)
def exe_sql_fixture():
    """执行用例前先执行 sql 语句（前置）"""
    fw_logger.debug("执行 SQL 前置操作")
    yield
    fw_logger.debug("关闭数据库连接")


@pytest.fixture(scope="class", autouse=False)
def all_class_fixture():
    """类级别前后置"""
    fw_logger.debug("类【前】处理")
    yield
    fw_logger.debug("类【后】处理")


@pytest.fixture(scope="session", autouse=True)
def setup_global_environment():
    """全局前置处理：
    1. 清空 extract.yaml
    2. 报告当前环境信息
    """
    current_env = config.current_env
    base_url = config.get_base_url()

    fw_logger.info(f"初始化测试环境: {current_env}")
    fw_logger.info(f"基础 URL: {base_url}")

    # 清空 extract.yaml，防止残留数据影响
    clear_extract_yaml()

    yield

    fw_logger.info("所有测试执行完毕，环境清理完成")
