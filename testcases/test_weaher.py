import jsonpath
import pytest

from commons.request_util import RequestUtil
from commons.extract_util import read_yaml, write_yaml


class AAAWeaher():

    def test_weaher(self, all_class_fixture, exe_sql_fixture, bbb):
        """
        {"reason":"查询成功!","result":{"city":"广州","realtime":{"temperature":"26","humidity":"82","info":"多云","wid":"01","direct":"西南风","power":"3-4级","aqi":"118"},"future":[{"date":"2026-04-19","temperature":"22/32℃","weather":"多云","wid":{"day":"01","night":"01"},"direct":"南风转微风"},{"date":"2026-04-20","temperature":"22/28℃","weather":"中雨转雷阵雨","wid":{"day":"08","night":"04"},"direct":"微风"},{"date":"2026-04-21","temperature":"22/28℃","weather":"多云转晴","wid":{"day":"01","night":"00"},"direct":"南风转微风"},{"date":"2026-04-22","temperature":"22/29℃","weather":"雷阵雨","wid":{"day":"04","night":"04"},"direct":"南风转微风"},{"date":"2026-04-23","temperature":"19/25℃","weather":"大雨转多云","wid":{"day":"09","night":"01"},"direct":"微风"}]},"error_code":0}
        """

        url = 'https://apis.juhe.cn/simpleWeather/query'
        method = 'get'
        datas = {
            'city': '广州',
            'key': 'd47d0716f8b4f06726b65d2c83d6258d',
        }
        # 发送请求
        res = RequestUtil().send_all_request(method=method, url=url, params=datas)
        result = res.json()
        city = jsonpath.jsonpath(result, "$.result.city")
        today = jsonpath.jsonpath(result, "$.result.future[0]")
        next_today = jsonpath.jsonpath(result, "$.result.future[1]")
        write_yaml({"city": city, "today": today, "next_today": next_today})

    def test_weaher2(self):
        print(11111111, read_yaml("city"))
        print(22222222, read_yaml("today"))
        today = read_yaml("today")
        print(today[0]['date'])
        print(today[0]['temperature'])