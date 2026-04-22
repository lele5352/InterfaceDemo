import re

import jsonpath

from commons.extract_util import write_yaml, read_yaml
from commons.request_util import RequestUtil


class TestLottery():
    def test_lottery_types(self):
        url = 'https://apis.juhe.cn/lottery/types'
        method = 'get'
        datas = {
            'key': '1353bc8292f5613be35c23315c1c71b4',
        }
        # 发送请求
        res = RequestUtil().send_all_request(method=method, url=url, params=datas)
        result = res.json()
        print(result)
        # 通过jsonpath获取返参相关数据
        ssq = jsonpath.jsonpath(result, "$.result[0]")
        write_yaml({"ssq": ssq})

    def test_lottery_query(self):
        url = 'https://apis.juhe.cn/lottery/query'
        method = 'post'
        datas = {
            'key': '1353bc8292f5613be35c23315c1c71b4',
            'lottery_id': read_yaml("ssq")[0]["lottery_id"]
        }
        # 发送请求
        res = RequestUtil().send_all_request(method=method, url=url, params=datas)
        # 通过正则获取相关信息
        result = res.text
        print(result)
        r = re.search('"reason":"(.*?)"', result)
        write_yaml({"reason": r[1]})