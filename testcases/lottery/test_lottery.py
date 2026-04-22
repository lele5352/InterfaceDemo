import re

import jsonpath
import pytest

import testcases
from commons.extract_util import write_yaml, read_yaml, read_testcase
from commons.request_util import RequestUtil


class AAALottery():

    # @pytest.mark.parametrize("caseinfo", read_testcase("../testcases/lottery/lottery_types.yl"))
    # @pytest.mark.parametrize("caseinfo", read_testcase("lottery_types.yl"))
    def test_lottery_types(self, caseinfo):
        url = caseinfo['request']['url']
        method = caseinfo['request']['method']
        params = caseinfo['request']['params']
        # 发送请求
        # res = RequestUtil().send_all_request(method=method, url=url, params=params)
        # result = res.json()
        result = {"reason":"查询成功","result":[{"lottery_id":"ssq","lot tery_name":"双色球","lottery_type_id":"1","remarks":"每周二、四、日开奖"},{"lottery_id":"dlt","lottery_name":"超级大乐透","lottery_type_id":"2","remarks":"每周一、三、六开奖"},{"lottery_id":"qlc","lottery_name":"七乐彩","lottery_type_id":"1","remarks":"每周一、三、五开奖"},{"lottery_id":"fcsd","lottery_name":"福彩3D","lottery_type_id":"1","remarks":"每日开奖"},{"lottery_id":"qxc","lottery_name":"七星彩","lottery_type_id":"2","remarks":"每周二、五、日开奖"},{"lottery_id":"pls","lottery_name":"排列3","lottery_type_id":"2","remarks":"每日开奖"},{"lottery_id":"plw","lottery_name":"排列5","lottery_type_id":"2","remarks":"每日开奖"}],"error_code":0}
        # 通过jsonpath获取返参相关数据
        ssq_id = jsonpath.jsonpath(result, "$.result[0]['lottery_id']")

        print(11111111, ssq_id[0])
        write_yaml({"ssq_id": ssq_id[0]})



    # def test_lottery_query(self):
    #     url = 'https://apis.juhe.cn/lottery/query'
    #     method = 'post'
    #     datas = {
    #         'key': '1353bc8292f5613be35c23315c1c71b4',
    #         'lottery_id': read_yaml("ssq")[0]["lottery_id"]
    #     }
    #     # 发送请求
    #     res = RequestUtil().send_all_request(method=method, url=url, params=datas)
    #     # 通过正则获取相关信息
    #     result = res.text
    #     print(result)
    #     r = re.search('"reason":"(.*?)"', result)
    #     write_yaml({"reason": r[1]})


if __name__ == '__main__':
    AAALottery().test_lottery_types
