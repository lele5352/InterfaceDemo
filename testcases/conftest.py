import pytest

from commons.extract_util import clear_yaml

"""
前后置：比如前置：链接数据库。后置：关闭关闭数据库。
1.conftest.py配置文件
特点1：它仅仅只用于放fixtrue（固件，夹具）的配置文件，名字是固定的。
特点2：它一般放在testcases下面，其它用例调用conftest里面的fixtrue，不需要导包。
2.fixture(固件，夹具)
@pytest.fixture(scope="作用域",autouse="True自动/False手动")
作用域：
function：每一个函数之前或之后执行
class：每一个类之前或之后执行
module：每一个模块之前或之后执行
session：整个项目之前或之后执
"""


@pytest.fixture(scope='function', autouse=False)
def exe_sql_fixture():
    print("执行用例前先执行sql语句")
    yield
    print("关闭数据库链接")


@pytest.fixture(scope='class', autouse=False)
def all_class_fixture():
    print("*****类【前】执行的代码")
    yield
    print("*****类【后】执行的代码")


# 每次执行项目之前清空extract_yaml文件内信息
@pytest.fixture(scope='session', autouse=True)
def clear_extract_yaml():
    clear_yaml()


@pytest.fixture(scope='function', autouse=False)
def bbb():
    yield
    print("bbbbbbbbbbbbb")
