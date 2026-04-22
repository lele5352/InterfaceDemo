from commons.request_util import RequestUtil
from commons.extract_util import extract_res_info, get_data
from commons.logger import logger


def stand_case_flow(test_case):
    """
    标准化测试用例执行流程
    :param test_case: case_obj对象
    :return: 执行结果（dict）
    """
    try:
        # 1. 初始化请求工具
        req_util = RequestUtil()

        # 2. 提取参数
        case_name = test_case.title
        request_info = test_case.request
        extract_info = test_case.extract
        validate_info = test_case.validate

        # 3. 发送请求

        res = req_util.send_all_request(**request_info)

        # 4. 提取响应数据（如需）
        if extract_info:
            extract_res_info(res, extract_info, case_name)

        # 5. 校验响应（如需）
        if validate_info:
            validate_result = True
            fail_reason = ""
            # 示例：校验状态码
            if 'status_code' in validate_info:
                expect_code = validate_info['status_code']
                actual_code = res.status_code
                if actual_code != expect_code:
                    validate_result = False
                    fail_reason = f"状态码校验失败，期望{expect_code}，实际{actual_code}"

            # 示例：校验响应字段（JSONPath）
            if 'json_rule' in validate_info and validate_result:
                json_rule = validate_info['json_rule']
                expect_value = validate_info['expect_value']
                actual_value = get_data('json', res.json(), json_rule)
                if actual_value != expect_value:
                    validate_result = False
                    fail_reason = f"JSON字段校验失败，期望{expect_value}，实际{actual_value}"

            if not validate_result:
                return {
                    'case_name': case_name,
                    'status': 'failed',
                    'reason': fail_reason,
                    'response': res.text
                }

        # 6. 执行成功
        logger.info(f"用例：【{case_name}】执行成功")
        return {
            'case_name': case_name,
            'status': 'success',
            'response': res.text,
            'status_code': res.status_code
        }
    except Exception as e:
        logger.error(f"用例执行异常：{str(e)}", exc_info=True)
        return {
            'case_name': test_case.get('case_name', '未命名用例'),
            'status': 'error',
            'reason': str(e)
        }
