"""
YAML 读写工具 - 统一管理所有 YAML 文件的读取和写入
"""

import os
from pathlib import Path
from typing import Any, Optional

import yaml

from commons.logger import logger
from commons.settings import PROJECT_ROOT

# extract.yaml 默认路径
EXTRACT_YAML_PATH = PROJECT_ROOT / "extract.yaml"


def read_yaml_file(file_path: str) -> Any:
    """读取 YAML 文件，返回 Python 对象

    Args:
        file_path: YAML 文件路径（支持绝对/相对路径）

    Returns:
        解析后的 Python 对象（dict/list/None）
    """
    path = Path(file_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / file_path

    if not path.exists():
        logger.warning(f"YAML 文件不存在: {path}")
        return None

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data
    except yaml.YAMLError as e:
        logger.error(f"YAML 解析失败 [{path}]: {e}")
        return None
    except Exception as e:
        logger.error(f"读取 YAML 失败 [{path}]: {e}", exc_info=True)
        return None


def write_yaml_file(file_path: str, data: Any, mode: str = "w"):
    """写入数据到 YAML 文件

    Args:
        file_path: YAML 文件路径
        data: 要写入的数据
        mode: 写入模式 ("w" 覆盖, "a" 追加)
    """
    path = Path(file_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / file_path

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, encoding="utf-8", mode=mode) as f:
            yaml.safe_dump(data, stream=f, allow_unicode=True, sort_keys=False)
        logger.debug(f"YAML 写入成功: {path}")
    except Exception as e:
        logger.error(f"YAML 写入失败 [{path}]: {e}", exc_info=True)


def append_to_yaml(file_path: str, data: dict):
    """追加数据到 YAML 文件（先读现有数据，再合并后写入）

    Args:
        file_path: YAML 文件路径
        data: 要追加的字典数据
    """
    path = Path(file_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / file_path

    existing = read_yaml_file(str(path)) or {}
    if isinstance(existing, list):
        existing = {}
    existing.update(data)
    write_yaml_file(str(path), existing, mode="w")
    logger.debug(f"追加数据到 YAML: {path}, 数据: {data}")


def clear_yaml_file(file_path: str):
    """清空 YAML 文件内容

    Args:
        file_path: YAML 文件路径
    """
    path = Path(file_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / file_path

    try:
        with open(path, encoding="utf-8", mode="w") as f:
            f.truncate()
        logger.debug(f"YAML 文件已清空: {path}")
    except Exception as e:
        logger.error(f"清空 YAML 失败 [{path}]: {e}", exc_info=True)


# ==================== extract.yaml 专用方法 ====================

def read_extract_yaml() -> dict:
    """读取 extract.yaml 文件，返回字典

    Returns:
        extract.yaml 中的键值对字典
    """
    data = read_yaml_file(str(EXTRACT_YAML_PATH))
    if data is None:
        return {}
    if isinstance(data, list):
        return {}
    return data


def write_extract_yaml(data: dict):
    """追加数据到 extract.yaml

    Args:
        data: 要追加的键值对字典
    """
    append_to_yaml(str(EXTRACT_YAML_PATH), data)


def get_extract_value(key: str) -> Any:
    """从 extract.yaml 获取指定 key 的值

    Args:
        key: 变量名

    Returns:
        变量值，未找到返回 None
    """
    data = read_extract_yaml()
    return data.get(key)


def clear_extract_yaml():
    """清空 extract.yaml 文件"""
    clear_yaml_file(str(EXTRACT_YAML_PATH))
