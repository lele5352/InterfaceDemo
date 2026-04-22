import requests


class RequestUtil:
    sess = requests.session()

    def send_all_request(self, *kwargs):
        res = self.sess.request(*kwargs)
        return res
