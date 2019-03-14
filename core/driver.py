import os
import requests
import selenium


class Driver:

    def __init__(self, entry='direct_http_mode'):
        self.cookie = ''
        self.proxy = ''
        self.entry = entry
        self.data = ''

    def http_get(self, url):
        response = requests.get(url)
        return response.text

    def http_post(self, url, data, json):
        response = requests.post(url, data, json)
        return response

    def open_url(self, url, method='get'):
        if self.entry == 'direct_http_mode':
            self.data = locals()['http' + method](url)

