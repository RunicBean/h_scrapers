import os
import requests
import selenium

from errors import GotInvalidResponseError


class Driver:

    def __init__(self, entry='direct_http_mode'):
        self.cookie = ''
        self.use_proxy = ''
        self.proxies = dict()
        self.entry = entry
        self._data = ''
        self.snapshot = list()
        self.headers = dict()
        self.headers['user-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        # self.proxies = {'http': 'http://25.123.23.175:9090',
        #                 'https': 'https://25.123.23.175:9090', }

    def http_get(self, url, headers=None):
        if headers:
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url, headers=self.headers, proxies=self.proxies)
        return response.text

    def http_post(self, url, data, json):
        response = requests.post(url, data, json, headers=self.headers, proxies=self.proxies)
        return response.text

    def open_url(self, url, method='get', *args, **kwargs):
        if self.entry == 'direct_http_mode':
            response_text = getattr(self, 'http_' + method)(url, *args, **kwargs)
        if not locals().get('response_text'):
            raise GotInvalidResponseError('entry mode does not exist. Expected: (direct_http_mode/webdriver_mode) Given: {}'.format(self.entry))
        if not response_text:
            raise GotInvalidResponseError('Nothing returned when open a url.')
        self.snapshot.append(response_text)
        self._data = response_text
        return self._data

    def set_referer(self, referer):
        self.headers['referer'] = referer

    def set_ua(self, ua):
        self.headers['user-agent'] = ua

    def set_proxies(self, proxies):
        self.proxies = proxies

    def get_source(self):
        return self._data

