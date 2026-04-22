from pathlib import Path

import allure
import pytest
from commons.main_util import stand_case_flow
from commons.model_util import verify_yaml
from commons.extract_util import read_testcase
from commons.logger import logger
from configs import PROJECT_NAME


# Allure 报告顶层目录
@allure.epic(PROJECT_NAME)
class TestAllCase:
    """自动加载YAML测试用例的测试类"""
    pass


def run_case(case_obj, yaml_path: Path):
    """
    统一用例执行入口
    :param case_obj: 校验后的用例对象
    :param yaml_path: YAML文件路径
    """
    # 动态绑定 Allure 报告信息
    if case_obj.feature:
        allure.dynamic.feature(case_obj.feature)
    if case_obj.story:
        allure.dynamic.story(case_obj.story)
    allure.dynamic.title(case_obj.title)

    # 执行核心用例流程
    logger.info(f"开始执行用例：{yaml_path.name} | 用例标题：{case_obj.title}")
    stand_case_flow(case_obj)
    logger.info(f"用例执行完成：{yaml_path.name}")


def create_testcase(yaml_path: Path):
    """
    为单个YAML文件生成 pytest 测试方法
    :param yaml_path: YAML文件路径对象
    :return: 测试方法
    """

    @pytest.mark.parametrize(
        "case_data",
        read_testcase(yaml_path),
        ids=[yaml_path.stem]  # 用例ID = 文件名
    )
    def test_func(self, case_data):
        # 日志打印
        logger.info(f"=" * 80)
        logger.info(f"加载用例文件：{yaml_path}")

        # YAML 格式校验
        case_obj = verify_yaml(case_data, yaml_path.name)

        # 执行用例
        run_case(case_obj, yaml_path)

    return test_func


# ===================== 自动扫描并动态注册用例 =====================
# 当前文件所在目录 = testcases 目录
TESTCASES_DIR = Path(__file__).parent
# 递归扫描所有 YAML 用例文件（支持 .yaml / .yml）
YAML_CASE_FILES = sorted(TESTCASES_DIR.rglob("*.yaml")) + sorted(TESTCASES_DIR.rglob("*.yml"))

# 动态给测试类添加方法
for yaml_file in YAML_CASE_FILES:
    # 生成唯一测试方法名
    test_method_name = f"test_{yaml_file.stem}"
    # 生成测试函数
    test_method = create_testcase(yaml_file)
    # 绑定到测试类
    setattr(TestAllCase, test_method_name, test_method)