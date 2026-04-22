"""
log.py - 自动化测试日志工具（开箱即用版）
使用方法：
    from log import logger

    logger.debug("调试信息")
    logger.info("关键步骤")
    logger.warning("警告信息")
    logger.error("错误信息")
"""

import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

# ==================== 私有变量（惰性初始化） ====================
_logger = None
_log_dir = "./logs"
if not os.path.exists(_log_dir):
    os.mkdir(_log_dir)


def _get_logger():
    """
    惰性初始化：仅在第一次调用时创建 logger
    """
    global _logger
    if _logger is not None:
        return _logger

    # 1. 创建日志目录
    if not os.path.exists(_log_dir):
        os.makedirs(_log_dir, exist_ok=True)

    # 2. 生成当天日志文件名
    log_file = os.path.join(_log_dir, f"{time.strftime('%Y-%m-%d_%H:%M:%S')}.log")

    # 3. 创建 logger 实例
    _logger = logging.getLogger("AutoTest")
    _logger.setLevel(logging.DEBUG)
    _logger.propagate = False  # 防止日志向上传播导致重复

    # 4. 定义格式
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 5. 控制台 Handler（INFO 级别，简洁输出）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

    # 6. 文件 Handler（DEBUG 级别，自动轮转）
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
            delay=True
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        _logger.addHandler(file_handler)
    except PermissionError:
        _logger.warning(f"无权限写入日志目录: {_log_dir}，仅输出到控制台")

    return _logger


def set_log_dir(path: str):
    """
    可选：自定义日志目录
    Usage: log.set_log_dir("./custom_logs")
    """
    global _log_dir
    _log_dir = path
    # 重置 logger，下次调用时会使用新路径
    global _logger
    _logger = None


# ==================== 公开接口 ====================
logger = _get_logger()

# ==================== 自测代码 ====================
if __name__ == "__main__":
    print(f"日志目录: {_log_dir}")
    logger.debug("这是一条 DEBUG 日志（仅在文件中可见）")
    logger.info("这是一条 INFO 日志")
    logger.warning("这是一条 WARNING 日志")
    logger.error("这是一条 ERROR 日志")

    print("\n✅ 日志测试完成，请检查以下位置：")
    print(f"   控制台输出：上方可见 INFO/WARNING/ERROR")
    print(f"   文件输出：{_log_dir}/{time.strftime('%Y-%m-%d')}.log")