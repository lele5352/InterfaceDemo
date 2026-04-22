import requests
from commons.logger import logger

class RequestUtil:

    # 在 commons 中实现单例模式，减少资源消耗
    sess = requests.session()

    def send_all_request(self, **kwargs):
        """
        发送HTTP请求，支持所有requests参数
        :param kwargs: method/url/params/data/json/headers/cookies/files等
        :return: requests.Response对象 | None
        """
        try:
            # 校验必填参数
            if not kwargs.get('method') or not kwargs.get('url'):
                logger.error("请求方法(method)和URL(url)为必填参数")
                return None

            # 统一方法名大写
            kwargs['method'] = kwargs['method'].upper()
            logger.info(f"发送{kwargs['method']}请求，URL：{kwargs['url']}")

            # 发送请求
            res = self.sess.request(**kwargs)
            logger.info(f"请求发送成功，响应状态码：{res.status_code}")
            return res
        except Exception as e:
            logger.error(f"请求发送失败：{str(e)}", exc_info=True)
            return None
