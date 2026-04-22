import os
import time
from dotenv import load_dotenv
import pytest

if __name__ == '__main__':

    # 在 Pytest 收集用例之前加载环境变量

    pytest.main()
    # time.sleep(3)
    # 生成测试报告
    # os.system("allure generate ./temps -o ./reports --clean")
