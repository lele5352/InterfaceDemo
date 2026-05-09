"""
热加载函数库 - 用户可在此文件中自定义函数，供 YAML 用例通过 ${函数名(参数)} 调用

使用示例:
  YAML:  ${random_phone()}
  YAML:  ${random_number(1, 100)}
  YAML:  ${current_date()}
  YAML:  ${uuid_str()}
"""

import random
import string
import time
import uuid
from datetime import datetime
from typing import Any


class DebugTalk:
    """热加载函数类，框架通过反射调用其中的方法"""

    # ==================== 随机数据生成 ====================

    def random_number(self, min_val: int = 0, max_val: int = 100) -> int:
        """生成指定范围内的随机整数

        Args:
            min_val: 最小值（默认 0）
            max_val: 最大值（默认 100）

        Returns:
            随机整数
        """
        return random.randint(int(min_val), int(max_val))

    def random_phone(self) -> str:
        """生成随机手机号（13/15/17/18/19 开头）

        Returns:
            11 位手机号字符串
        """
        prefixes = ["13", "15", "17", "18", "19"]
        prefix = random.choice(prefixes)
        suffix = "".join(random.choices(string.digits, k=9))
        return prefix + suffix

    def random_string(self, length: int = 8) -> str:
        """生成随机字符串（字母+数字）

        Args:
            length: 字符串长度（默认 8）

        Returns:
            随机字符串
        """
        return "".join(random.choices(string.ascii_letters + string.digits, k=int(length)))

    def uuid_str(self) -> str:
        """生成 UUID 字符串（无连字符）

        Returns:
            32 位十六进制字符串
        """
        return uuid.uuid4().hex

    def uuid_with_hyphen(self) -> str:
        """生成带连字符的 UUID

        Returns:
            标准 UUID 格式
        """
        return str(uuid.uuid4())

    # ==================== 日期时间 ====================

    def current_date(self, fmt: str = "%Y-%m-%d") -> str:
        """获取当前日期

        Args:
            fmt: 日期格式（默认 %Y-%m-%d）

        Returns:
            格式化日期字符串
        """
        return datetime.now().strftime(fmt)

    def current_time(self, fmt: str = "%H:%M:%S") -> str:
        """获取当前时间

        Args:
            fmt: 时间格式（默认 %H:%M:%S）

        Returns:
            格式化时间字符串
        """
        return datetime.now().strftime(fmt)

    def timestamp(self) -> int:
        """获取当前时间戳（秒）

        Returns:
            10 位时间戳
        """
        return int(time.time())

    def timestamp_ms(self) -> int:
        """获取当前时间戳（毫秒）

        Returns:
            13 位时间戳
        """
        return int(time.time() * 1000)

    def format_time(self, days: int = 0, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """获取偏移后的格式化时间

        Args:
            days: 偏移天数（+1 明天，-1 昨天）
            fmt: 日期格式

        Returns:
            格式化日期字符串
        """
        from datetime import timedelta
        target = datetime.now() + timedelta(days=int(days))
        return target.strftime(fmt)

    # ==================== 数据读取 ====================

    def get_extract_data(self, key: str) -> Any:
        """从 extract.yaml 读取已提取的变量值

        Args:
            key: 变量名

        Returns:
            变量值，未找到返回 None
        """
        from commons.yaml_util import get_extract_value
        return get_extract_value(key)
