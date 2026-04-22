# import re
#
# import jsonpath
# import yaml
#
#
# # 写入数据
# def write_yaml(data):
#     with open('./extract.yaml', encoding='utf-8', mode='a+') as f:
#         yaml.safe_dump(data, stream=f, allow_unicode=True)
#
#
# # 读取数据
# def read_yaml(key):
#     with open('./extract.yaml', encoding='utf-8', mode='r') as f:
#         all_value = yaml.safe_load(f)
#         return all_value[key]
#
#
# # 清空
# def clear_yaml():
#     with open('./extract.yaml', encoding='utf-8', mode='w') as f:
#         pass
#
#
# # 读取测试用例
# def read_testcase(path):
#     with open(path, encoding='utf-8', mode='r') as f:
#         all_value = yaml.safe_load(f)
#         return all_value
#
#
# def get_data(method, obj, rule):
#     if method == "json":
#         return jsonpath.jsonpath(obj, rule)
#     elif method == "text":
#         return re.search(rule, obj)
#     else:
#         print("获取数据方法有误，仅支持json或text")


import re
import os
import jsonpath
import yaml
from commons.logger import logger


# 写入数据到YAML
def write_yaml(data, file_path='./extract.yaml'):
    """
    写入数据到YAML文件（追加模式）
    :param data: 要写入的数据（dict/list等）
    :param file_path: YAML文件路径
    :return: bool
    """
    try:
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(file_path, encoding='utf-8', mode='a+') as f:
            yaml.safe_dump(data, stream=f, allow_unicode=True, sort_keys=False)
        logger.info(f"数据写入{file_path}成功：{data}")
        return True
    except Exception as e:
        logger.error(f"数据写入{file_path}失败：{str(e)}", exc_info=True)
        return False


# 读取YAML指定key的值
def read_yaml(key, file_path='./extract.yaml'):
    """
    读取YAML文件中指定key的值
    :param key: 要读取的键
    :param file_path: YAML文件路径
    :return: 对应值 | None
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"YAML文件不存在：{file_path}")
            return None

        with open(file_path, encoding='utf-8', mode='r') as f:
            all_value = yaml.safe_load(f) or {}  # 避免文件为空时报错
            if key not in all_value:
                logger.warning(f"YAML文件中未找到key：{key}")
                return None
            return all_value[key]
    except Exception as e:
        logger.error(f"读取YAML失败：{str(e)}", exc_info=True)
        return None


# 清空YAML文件
def clear_yaml(file_path='./extract.yaml'):
    """清空YAML文件内容"""
    try:
        with open(file_path, encoding='utf-8', mode='w') as f:
            f.truncate()  # 明确清空文件
        logger.info(f"YAML文件已清空：{file_path}")
        return True
    except Exception as e:
        logger.error(f"清空YAML失败：{str(e)}", exc_info=True)
        return False


# 读取测试用例（YAML格式）
def read_testcase(path):
    """
    读取测试用例文件（支持单文件/目录）
    :param path: 用例文件路径或目录路径
    :return: 用例数据列表 | None
    """
    try:
        test_cases = []
        path = str(path)
        # 如果是目录，遍历所有YAML文件
        if os.path.isdir(path):
            for file_name in os.listdir(path):
                if file_name.endswith(('.yaml', '.yml')):
                    file_path = os.path.join(path, file_name)
                    with open(file_path, encoding='utf-8', mode='r') as f:
                        case = yaml.safe_load(f)
                        if case:
                            test_cases.append(case)
        # 如果是文件，直接读取
        elif os.path.isfile(path) and path.endswith(('.yaml', '.yml')):
            with open(path, encoding='utf-8', mode='r') as f:
                case = yaml.safe_load(f)
                if case:
                    test_cases.append(case)
                    logger.info("读取测试用例:{0}".format(case))
                else:
                    logger.info()
        else:
            logger.error(f"用例路径无效（非YAML文件/目录）：{path}")
            return None
        logger.info(f"读取测试用例成功，共{len(test_cases)}条")
        return test_cases
    except Exception as e:
        logger.error(f"读取测试用例失败：{str(e)}", exc_info=True)
        return None


# 提取响应数据（JSONPath/正则）
def get_data(method, obj, rule):
    """
    提取数据
    :param method: 提取方式（json/text）
    :param obj: 数据源（JSON响应体/文本）
    :param rule: 提取规则（JSONPath表达式/正则表达式）
    :return: 提取结果 | None
    """
    try:
        if method == "json":
            result = jsonpath.jsonpath(obj, rule)
            # JSONPath返回False表示无匹配，统一返回None
            if result:
                return result
            else:
                logger.error(f"【{method}】数据提取失败！！！")
                return None
        elif method == "text":
            result = re.search(rule, obj)
            if result:
                return result
            else:
                logger.error(f"【{method}】数据提取失败！！！")
                return None
        else:
            logger.error(f"不支持的提取方法：{method}（仅支持json/text）")
            return None
    except Exception as e:
        logger.error(f"数据提取失败：{str(e)}", exc_info=True)
        return None


def extract_res_info(res, extract_info, case_name):
    """
    提取接口内关联字段信息并保存
    :param res: 响应结果
    :param extract_info:
    :param case_name:
    :return:
    """

    for key, extract_conf in extract_info.items():
        method = extract_conf[0]
        rule = extract_conf[1]
        index = extract_conf[2]
        data = res.json() if method == 'json' else res.text
        extract_value = get_data(method, data, rule)
        if extract_value:
            extract_result = {}
            extract_result[key] = extract_value[index]
            write_yaml(extract_result)  # 写入YAML
    return
