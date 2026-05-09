"""
运行入口 - 支持命令行参数和环境选择

pytest 参数（-m 标记、--alluredir、-q 等）统一由 pytest.ini 的 addopts 管理。
如需临时覆盖，直接运行 pytest 命令（可 --override-ini 覆盖 addopts）。

用法:
    python run.py                 # 默认 test 环境
    python run.py --env prod      # 生产环境
"""

import argparse
import subprocess
import sys

from commons.logger import logger
from commons.settings import config


def parse_args():
    """解析命令行参数

    --env: 环境选择 (dev/test/prod)，默认 test
    未知参数（pytest 专属）直接忽略，不阻塞运行
    """
    parser = argparse.ArgumentParser(description="零代码接口自动化测试框架")
    parser.add_argument("--env", default="test", choices=["dev", "test", "prod"],
                        help="测试环境 (dev/test/prod)，默认 test")
    args, _ = parser.parse_known_args()
    return args


def run_pytest() -> int:
    """执行 pytest 测试（pytest.ini 的 addopts 自动生效）"""
    import pytest
    return pytest.main()


def generate_allure_report(alluredir: str = "./temps", reportdir: str = "./reports"):
    """生成 Allure HTML 报告

    Args:
        alluredir: Allure 原始结果目录
        reportdir: 报告输出目录
    """
    try:
        result = subprocess.run(
            ["allure", "generate", alluredir, "-o", reportdir, "--clean"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            logger.info(f"Allure 报告已生成: {reportdir}")
        else:
            logger.error(f"Allure 生成失败: {result.stderr.strip()}")
    except FileNotFoundError:
        logger.warning("未安装 Allure 命令行工具，跳过报告生成。")
        logger.warning("安装方式: brew install allure")


if __name__ == '__main__':
    args = parse_args()

    # 切换环境
    config.set_env(args.env)

    # 执行测试（pytest.ini 的 addopts 自动生效）
    exit_code = run_pytest()

    # 生成报告
    generate_allure_report()

    sys.exit(exit_code)
