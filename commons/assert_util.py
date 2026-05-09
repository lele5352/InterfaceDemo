"""
响应断言引擎 - 支持 equals 精确匹配和 contains 包含匹配
"""

from numbers import Number

import jsonpath
from requests import Response


class ResponseValidator:
    """响应结果校验器 - 适配 Pytest 原生断言"""

    def __init__(self, response: Response):
        self.res = response
        self.actual_status_code = response.status_code
        try:
            self.res_json = response.json()
        except ValueError:
            self.res_json = None
        self.res_text = response.text

    def validate(self, validate_info: dict):
        """
        执行校验

        注意：这里不返回 (bool, str)，而是直接让断言失败抛出 AssertionError
        Pytest 会捕获这个异常并显示在报告中

        validate_info 格式:
            equals:
                断言状态码为200: [200, status_code]
            contains:
                断言包含成功: [成功, text]
        """
        if not validate_info:
            return

        for assert_type, rules in validate_info.items():
            if not isinstance(rules, dict):
                continue

            for assert_desc, check_pair in rules.items():
                if not isinstance(check_pair, list) or len(check_pair) != 2:
                    continue

                expect_val, actual_expr = check_pair
                actual_val = self._get_actual_value(actual_expr)

                if assert_type == "equals":
                    self._assert_equals(actual_val, expect_val, assert_desc)

                elif assert_type == "contains":
                    self._assert_contains(actual_val, expect_val, assert_desc)

    def _assert_equals(self, actual, expected, desc: str):
        """精确匹配断言 — 类型不同直接判失败，避免 str() 强转掩盖类型不匹配"""
        # 如果实际值为 None（提取失败或字段不存在），直接失败
        if actual is None:
            raise AssertionError(f"{desc} (实际值为 None, 期望: {expected})")

        # 允许数字类型的混用 (int vs float)，其他类型必须一致
        if isinstance(actual, Number) and isinstance(expected, Number):
            assert actual == expected, \
                f"{desc} (期望: {expected}, 实际: {actual})"
        else:
            assert type(actual) == type(expected), \
                f"{desc} (类型不匹配: 实际={type(actual).__name__}, 期望={type(expected).__name__})"
            assert actual == expected, \
                f"{desc} (期望: {expected}, 实际: {actual})"

    def _assert_contains(self, actual, expected, desc: str):
        """包含匹配断言"""
        if actual is None:
            raise AssertionError(f"{desc} (实际值为 None, 期望包含: {expected})")

        actual_str = str(actual)
        expect_str = str(expected)
        assert expect_str in actual_str, \
            f"{desc} (期望包含: '{expect_str}', 实际: '{actual_str[:100]}...')"

    def _get_actual_value(self, expr: str):
        """解析实际值表达式

        支持:
            status_code — 响应状态码
            text        — 响应文本
            json        — 完整 JSON 响应
            $.xxx.xxx   — JSONPath 表达式
            其他        — 作为普通字符串值
        """
        if expr == "status_code":
            return self.actual_status_code
        elif expr == "text":
            return self.res_text
        elif expr == "json":
            return self.res_json
        elif expr.startswith("$."):
            if not self.res_json:
                return None
            result = jsonpath.jsonpath(self.res_json, expr)
            return None if result is False else result[0]
        return expr
