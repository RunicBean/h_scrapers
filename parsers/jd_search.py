import json
import math
import time
import urllib
import requests
from copy import copy

import template
from core import web_utils
from core import eutils
from core import driver
from parsers import BaseSearchParser
from errors import TemplatesNotMatched


class Parser(BaseSearchParser):

    def __init__(self):
        self.store = 'jd'
        self.type = 'search'

    @staticmethod
    def merge_tags(tags, new_tag):
        if not new_tag:
            return tags
        if not tags:
            return new_tag
        else:
            return '|'.join(tags.split('|') + [new_tag])

    @staticmethod
    def norm_stock(stock, price):
        if (price and not eutils.to_float(price)) or u'不支持配送' in stock:
            return 'Void'
        elif u'无货' in stock:
            return 'Out of stock'
        else:
            return 'In stock'

    @staticmethod
    def get_product_template():
        return [
            ('title', 'mandatory',
             (('.//div[contains(@class, "p-name")]/a/em', 'ptext'),
              ('.//div[@class="gl-act-title"]/strong', 'ptext'),
              ('.//div[@class="jGoodsInfo"]/div[@class="jDesc"]/a', 'ptext'),)),
            ('url', '',
             (('.//div[contains(@class, "p-name")]/a/@href', 'url'),
              ('.//div[@class="gl-act-enter"]/a/@href', 'url'),
              ('.//div[@class="jGoodsInfo"]/div[@class="jDesc"]/a/@href', 'url'),)),
            ('price', '',
             (('.//div[contains(@class, "p-price")]/strong/i', 'text'),
              ('.//div[contains(@class, "p-price")]/strong/@data-price', 'text'),)),
            ('primary_image', 'mandatory',
             (('.//div[contains(@class, "p-img")]/a/img/@source-data-lazy-img', 'url'),
              ('.//div[contains(@class, "p-img")]/a/img/@data-lazy-img', 'url'),
              ('.//div[contains(@class, "p-img")]/a/img/@src', 'url'),
              ('.//div[@class="gl-act-img"]/a/img/@source-data-lazy-img', 'url'),
              ('.//div[@class="gl-act-img"]/a/img/@data-lazy-img', 'url'),
              ('.//div[@class="gl-act-img"]/a/img/@src', 'url'),
              ('.//div[@class="jPic"]//img', 'attrs:original'),)),
            ('sub_store_name', '', (('.//div[contains(@class, "p-shop")]//a', 'attrs:title'),)),
            ('sub_store_url', '', (('.//div[contains(@class, "p-shop")]//a/@href', 'url'),)),
            ('availability', '', (('.//div[@class="p-stock"]', 'text'),)),
            ('tags', '', (('.//div[contains(@class, "p-icons")]/i', 'text'),)),
            ('paid', '', (('.//span[@class="p-promo-flag"]', 'text'),)),
            ('jd-plus', '', (('.//span[contains(@class, "price-plus")]', 'value:PLUS'),)),
            ('p-tag', '', (('.//span[@class="p-tag"]', 'text'),)),
            ('rpc', '', (('.//div[contains(@class, "p-price")]/strong', 'attrs:class'),
                         ('.//div[@class="jPic"]/span', 'attrs:data-id'),)),
        ]

    @staticmethod
    def build_search_url(scrape_params, page, next_start):

        first_party_only = scrape_params.get('first_party_only')
        sort_by = scrape_params.get('sort_by')
        in_stock_only = scrape_params.get('in_stock_only')
        include_out_of_stock = scrape_params.get('include_out_of_stock')
        global_product = scrape_params.get('global_product')
        keyword = scrape_params['search_term']
        quoted_keyword = urllib.parse.quote(keyword)

        search_url = 'https://search.jd.com/s_new.php?keyword={}&&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&stock=1&page={}&s={}&'.format(
            quoted_keyword, page, next_start)

        if sort_by == 'Sales':
            search_url += '&psort=3'
        if first_party_only == 'Y':
            search_url += '&wtype=1'
        if in_stock_only == 'Y':
            search_url += '&stock=1'
        if include_out_of_stock == 'Y':
            search_url += '&qrst=1'
        if global_product == 'Y':
            search_url += '&gp=1'

        if int(page) % 2 == 0:
            return search_url + '&scrolling=y'
        else:
            return search_url + '&click=0'

    @staticmethod
    def parse_one_sku(scrape_params, sku, element, rpc_seller_map):
        parsed_sku = template.parse_elements_xpath(element, Parser.get_product_template())
        if not parsed_sku:
            raise TemplatesNotMatched('Keyword: {} Params: {}'.format(scrape_params['search_term'], str(scrape_params)))
        sku.update(parsed_sku)

        sku['rpc'] = sku['rpc'][2:]
        sku['availability'] = Parser.norm_stock(sku['availability'], sku['price'])
        if 'ccc-x.jd.com' in sku['url']:
            sku['url'] = 'http://item.jd.com/{}.html'.format(sku['rpc'])
            sku['tags'] = Parser.merge_tags(sku['tags'], 'Paid')

        sku['url'] = sku['url'].split('?')[0]
        sku['tags'] = Parser.merge_tags(sku['tags'], sku['jd-plus'])
        sku['tags'] = Parser.merge_tags(sku['tags'], sku['p-tag'])
        if not sku['sub_store_name']:
            try:
                sku['sub_store_name'] = rpc_seller_map[sku['rpc']]
            except KeyError:
                sku['sub_store_name'] = u'京东自营'

        return sku

    def parse(self, driver, params):

        self.param_validate(params)
        keyword = params['search_term']
        self.results = list()
        total_paid = 0
        flag = (1, 1)
        sku_limit = int(params['limit'])

        while flag[1] < int(params['limit']):
            time.sleep(3)
            param_next_page = flag[0]
            surl = self.build_search_url(params, flag[0], flag[1])
            driver.set_referer(surl.replace('s_new.php', 'Search'))
            driver.open_url(surl)

            # Parse SKU details
            rpc_list = []
            rpc_seller_map = dict()
            lis = template.parse_html(driver.get_source().replace('<div耐克阿迪达斯乔丹', ''), '//li[@class="gl-item"]')

            # get rpc_seller_map
            for li in lis:

                tabs = li.xpath('.//div[contains(@class, "tab-content-item")]')
                sku_elements = tabs or [li]
                for e in sku_elements:
                    if len(e):
                        rpc = template.extract_value(e, './/div[contains(@class, "p-price")]/strong', 'attrs:class')
                        if rpc:
                            rpc_list.append(rpc[2:])

            seller_url = 'https://chat1.jd.com/api/checkChat?pidList={}&callback=jQuery2864087'.format(
                ','.join(rpc_list))
            response = requests.get(seller_url, headers={'referer': surl.replace('s_new.php', 'Search')}).text
            json_objs = json.loads(response.replace('jQuery2864087(', '').replace(');', ''))
            for obj in json_objs:
                if 'seller' in obj:
                    rpc_seller_map[str(obj['pid'])] = obj['seller']

            for li in lis:

                tabs = li.xpath('.//div[contains(@class, "tab-content-item")]')
                sku_elements = tabs or [li]
                tab_data = []

                sku = {
                    'store': params['store'],
                    'geo': params['geo'],
                    'keyword': keyword,
                    'scrape_keyword': keyword,
                    'harvested_url': surl,
                    'page': int(math.ceil(param_next_page / 2.0)),
                }
                for e in sku_elements:
                    tab_sku = Parser.parse_one_sku(params, copy(sku), e, rpc_seller_map)
                    if tab_data:
                        tab_sku['sub_store_name'] = tab_data[0]['sub_store_name']
                        tab_sku['sub_store_url'] = tab_data[0]['sub_store_url']
                    tab_data.append(tab_sku)

                for tr in tab_data:
                    if 'sequence' not in tr:
                        continue
                    if 'Paid' in tr['tags']:
                        total_paid += 1
                        tr['organic_sequence'] = ''
                    else:
                        tr['organic_sequence'] = tr['sequence'] - total_paid

                    tr['total_paid'] = total_paid
                self.results.extend(tab_data)

                if len(tab_data) - total_paid >= sku_limit:
                    break

            page_params = eutils.find_str(driver.get_source(), 'SEARCH\.page_html\((.*?)\)')[0]
            param_next_start = int(page_params.split(',')[4])
            param_next_page = int(page_params.split(',')[0]) + 1
            total_pages = int(page_params.split(',')[1])
            if param_next_page > total_pages:
                print('All results loaded. Exit')
                break
            else:
                flag = (param_next_page, param_next_start)

        return self.results
