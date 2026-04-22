from commons.request_util import RequestUtil


class TestWeaher():

    def test_weaher(self):
        url = 'https://apis.juhe.cn/simpleWeather/query'
        method = 'get'
        datas = {
            'city': '广州',
            'token': 'd47d0716f8b4f06726b65d2c83d6258d',
        }
        res = RequestUtil.send_all_request(url=url, method=method, json=datas)
        print(res.json())
