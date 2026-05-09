"""
测试用例发现与加载引擎 - 扫描 YAML 文件并构建 TestCase 对象
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from commons.logger import logger
from commons.model_util import TestCaseObj, build_test_case_obj, validate_case_data
from commons.settings import PROJECT_ROOT


def discover_yaml_files(root_dir: str = "testcases") -> List[Path]:
    """递归扫描 testcases 目录，发现所有 .yaml/.yml 文件

    Args:
        root_dir: 测试用例根目录（相对于项目根目录）

    Returns:
        YAML 文件路径列表
    """
    base_path = PROJECT_ROOT / root_dir
    if not base_path.exists():
        logger.warning(f"测试用例目录不存在: {base_path}")
        return []

    yaml_files = sorted(base_path.rglob("*.yaml")) + sorted(base_path.rglob("*.yml"))
    logger.info(f"发现 {len(yaml_files)} 个 YAML 用例文件: {base_path}")
    return yaml_files


def load_yaml_cases(yaml_path: Path) -> List[Dict[str, Any]]:
    """加载单个 YAML 文件中的所有测试用例

    Args:
        yaml_path: YAML 文件路径

    Returns:
        原始 YAML 解析后的用例字典列表
    """
    if not yaml_path.exists():
        logger.error(f"YAML 文件不存在: {yaml_path}")
        return []

    from commons.yaml_util import read_yaml_file
    data = read_yaml_file(str(yaml_path))
    if data is None:
        return []

    cases = data if isinstance(data, list) else [data]
    logger.info(f"加载 YAML 文件: {yaml_path}, {len(cases)} 个用例")
    return cases


def parse_test_case(raw_case: Dict[str, Any], yaml_filename: str) -> Optional[TestCaseObj]:
    """校验并构建 TestCaseObj 对象

    Args:
        raw_case: 原始 YAML 解析后的用例字典
        yaml_filename: YAML 文件名（用于日志）

    Returns:
        校验通过返回 TestCaseObj，失败返回 None
    """
    is_valid, errors = validate_case_data(raw_case)
    if not is_valid:
        logger.error(f"用例校验失败 [{yaml_filename}]: {errors}")
        return None

    case_obj = build_test_case_obj(raw_case)
    logger.debug(f"用例加载成功: [{case_obj.feature}] {case_obj.title}")
    return case_obj


def discover_and_parse(root_dir: str = "testcases") -> List[TestCaseObj]:
    """一站式发现并解析所有 YAML 用例

    此函数供 main_util.py 使用，一次调用即可获得所有已校验的用例对象

    Args:
        root_dir: 测试用例根目录

    Returns:
        TestCaseObj 列表
    """
    all_cases = []
    yaml_files = discover_yaml_files(root_dir)

    for yaml_path in yaml_files:
        raw_cases = load_yaml_cases(yaml_path)
        for raw in raw_cases:
            case_obj = parse_test_case(raw, yaml_path.name)
            if case_obj is not None:
                all_cases.append(case_obj)

    logger.info(f"共解析 {len(all_cases)} 个有效测试用例")
    return all_cases
