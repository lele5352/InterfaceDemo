"""
动态测试注册引擎 - 扫描 YAML 文件并动态生成 pytest 测试函数
"""

import os
from pathlib import Path

import allure
import pytest
import yaml

from commons.logger import logger
from commons.main_util import execute_test_case
from commons.model_util import verify_yaml
from commons.request_util import request_engine
from commons.settings import config
from commons.ddt_util import guess_parametrize


# ==================== YAML 用例读取 ====================

def read_testcase(path):
    """
    读取测试用例文件（支持单文件/目录）
    :param path: 用例文件路径或目录路径
    :return: 用例数据列表 | None
    """
    try:
        test_cases = []
        path_str = str(path)
        if os.path.isdir(path_str):
            for file_name in sorted(os.listdir(path_str)):
                if file_name.endswith(('.yaml', '.yml')):
                    file_path = os.path.join(path_str, file_name)
                    with open(file_path, encoding='utf-8', mode='r') as f:
                        case = yaml.safe_load(f)
                        if case:
                            test_cases.extend(case if isinstance(case, list) else [case])
        elif os.path.isfile(path_str) and path_str.endswith(('.yaml', '.yml')):
            with open(path_str, encoding='utf-8', mode='r') as f:
                case = yaml.safe_load(f)
                if case:
                    test_cases.extend(case if isinstance(case, list) else [case])
                    logger.info("读取测试用例:{0}".format(case))
                else:
                    logger.error(f"用例路径无效：{path_str}")
                    return None
        else:
            logger.error(f"用例路径无效（非YAML文件/目录）：{path_str}")
            return None

        logger.info(f"读取测试用例成功，共{len(test_cases)}条")
        return test_cases
    except Exception as e:
        logger.error(f"读取测试用例失败：{str(e)}", exc_info=True)
        return None


# ==================== 单用例执行 ====================

def _run_single_case(case, yaml_path):
    """校验并执行单个 YAML 用例"""
    case_obj_or_error = verify_yaml(case, yaml_path.name)
    if case_obj_or_error is None or (isinstance(case_obj_or_error, tuple) and case_obj_or_error[0] is False):
        pytest.skip(f"用例 YAML 校验失败: {yaml_path.name}")

    case_obj = case_obj_or_error

    allure.dynamic.feature(case_obj.feature)
    allure.dynamic.story(case_obj.story)
    allure.dynamic.title(case_obj.title)

    logger.info(f"开始执行用例：{yaml_path.name} | {case_obj.title}")
    execute_test_case(case_obj)


# ==================== 动态测试生成 ====================

def creat_testcase(yaml_path):
    """为 YAML 文件动态创建 pytest 测试函数"""
    raw_cases = read_testcase(yaml_path)
    if not raw_cases:
        return None

    first_case = raw_cases[0] if isinstance(raw_cases, list) else raw_cases
    parametrize_data = first_case.get("parametrize") if isinstance(first_case, dict) else None

    # ========== 参数化版本 ==========
    if parametrize_data:
        expanded = guess_parametrize(parametrize_data)
        if expanded:
            param_names, param_values = expanded
            # 将多组参数打包为单个 dict 进行 parametrize
            packed_values = [dict(zip(param_names, vals)) for vals in param_values]

            @pytest.mark.parametrize("ddt_context", packed_values)
            def parametrized_test(self, ddt_context):
                request_engine.set_parametrize_context(ddt_context)
                try:
                    for case in raw_cases:
                        _run_single_case(case, yaml_path)
                finally:
                    request_engine.set_parametrize_context(None)

            return parametrized_test

    # ========== 非参数化版本 - 在函数体内读取 YAML ==========
    def test_func(self):
        """动态注册的 YAML 测试用例"""
        yaml_path_local = yaml_path  # 闭包持有
        cases = read_testcase(yaml_path_local)
        if not cases:
            pytest.skip(f"YAML 文件为空: {yaml_path_local.name}")
        for case in cases:
            _run_single_case(case, yaml_path_local)

    return test_func


# ==================== 注册用例到 TestAllCase ====================

testcases_path = Path(__file__).parent
yaml_case_list = list(testcases_path.glob("**/*.yaml"))
yaml_case_list.sort()

project_name = config.get_config("PROJECT_NAME", "XX接口自动化测试")


@allure.epic(project_name)
class TestAllCase:
    """动态注册的 YAML 测试用例"""
    pass


for yaml_path in yaml_case_list:
    _tf = creat_testcase(yaml_path)
    if _tf:
        test_name = "test_" + yaml_path.stem
        setattr(TestAllCase, test_name, _tf)
