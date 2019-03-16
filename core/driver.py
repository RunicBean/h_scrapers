import os
import requests
import selenium


class Driver:

    def __init__(self, entry='direct_http_mode'):
        self.cookie = ''
        self.use_proxy = ''
        self.entry = entry
        self.data = ''
        self.headers = dict()
        self.headers['user-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'

    def http_get(self, url):
        response = requests.get(url, headers=self.headers)
        return response.text

    def http_post(self, url, data, json):
        response = requests.post(url, data, json, headers=self.headers)
        return response.text

    def open_url(self, url, method='get'):
        if self.entry == 'direct_http_mode':
            self.data = getattr(self, 'http_' + method)(url)

    def set_referer(self, referer):
        self.headers['referer'] = referer

    def set_ua(self, ua):
        self.headers['user-agent'] = ua

    def get_source(self):
        return self.data

