from pathlib import Path

import allure
import pytest
from commons.main_util import stand_case_flow
from commons.model_util import verify_yaml

from commons.extract_util import read_testcase
from commons.logger import logger
from configs import PROJECT_NAME


# 设置Allure报告的根目录名称（项目名称）
@allure.epic(PROJECT_NAME)
class TestAllCase():
    pass


# 根据一个yaml的路径创建一个测试用例的函数，并且返回这个函数
def creat_testcase(yaml_path):
    @pytest.mark.parametrize("caseinfo", read_testcase(yaml_path))
    def func(self, caseinfo):
        if isinstance(caseinfo, list):
            for case in caseinfo:
                logger.info(f"YAML_PATH: {yaml_path}")
                # 校验yaml中的数据
                case_obj = verify_yaml(case, yaml_path.name)
                # 定制Allure报告
                allure.dynamic.feature(case_obj.feature)
                allure.dynamic.story(case_obj.story)
                allure.dynamic.title(case_obj.title)
                # 用例的标准化流程
                logger.info(f"开始执行用例：{yaml_path.name} | 用例标题：{case_obj.title}")
                stand_case_flow(case_obj)
        else:

            logger.info(r"YAML_PATH: {0}".format(yaml_path))

            # 校验yaml中的数据
            case_obj = verify_yaml(caseinfo, yaml_path.name)
            # 定制Allure报告
            allure.dynamic.feature(case_obj.feature)
            allure.dynamic.story(case_obj.story)
            allure.dynamic.title(case_obj.title)
            # 用例的标准化流程
            logger.info(f"开始执行用例：{yaml_path.name} | 用例标题：{case_obj.title}")
            stand_case_flow(case_obj)
    return func

# 循环获取所有的yaml文件（一个yaml生成一个测试用例，然后把测试用例放到TestAllCase类下）
testcases_path = Path(__file__).parent  #获得testcases的路径
yaml_case_list = list(testcases_path.glob("**/*.yaml"))
yaml_case_list.sort()
for yaml_path in yaml_case_list:
    # 通过反射，循环每执行一次就生产一个函数，然后把这个函数加入到TestAllCase下面
    setattr(TestAllCase, "test_"+yaml_path.stem, creat_testcase(yaml_path))