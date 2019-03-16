import re
import json
import execjs

import template
from core import eutils
from core import web_utils
from errors import InputError
from parsers import BaseParser

# final var
STORE = 'jd'
TYPE = 'details'


class Parser(BaseParser):

    @property
    def store(self):
        return 'jd'

    @property
    def type(self):
        return 'details'

    def get_primary_secondary_images(self, source):
        image_list = eutils.find_str(source, r'\s+imageList:\s*\[(.+?)\]')
        secondary_image_text = template.extract_value(source,
                                                      '//div[@id="spec-list" and @class="spec-items"]/ul[@class="lh"]/li/img',
                                                      'attrs:data-url')
        image_base = '//img10.360buyimg.com/n1/'
        if image_list:
            images = [web_utils.normalize_url(image_base + i.replace('"', '')) for i in image_list[0].split(',')]
        else:
            src = eutils.find_str(source, r'\s+src:\s*(.+?),')[0]
            images = [web_utils.normalize_url(image_base + src)]
        primary_image = images[0].replace("'", '')
        secondary_image = '|'.join(images[1:]) if len(images) > 1 else ''
        if not secondary_image:
            if secondary_image_text:
                secondary_image = '|'.join([image_base + img for img in secondary_image_text.split('|')])
        return [primary_image, secondary_image]

    def get_trasaction(self, driver, sku_id, area_id, vender_id, cat_id):
        url = 'http://c0.3.cn/stock?skuId={}&area={}&venderId={}&cat={}&extraParam={{"originid":"1"}}'
        real_url = url.format(sku_id, area_id, vender_id, cat_id)
        retries = 0
        driver.set_referer(self.oneline['param_url'])
        while retries < 5:
            driver.open_url(real_url)
            details = json.loads(driver.get_source())['stock']
            if 'skuState' in details:
                break
            driver.use_proxy = True
            # driver.set_proxy(use_new_proxy=True)
            retries += 1
        sku_details = dict()
        if details['skuState'] == 0:
            avail = u'该商品已下柜'
        else:
            avail = eutils.remove(details['stockDesc'], '<.+?>')
            sku_details['price'] = eutils.get_from_json_by_string(details, 'jdPrice.p')
            sku_details['list_price'] = eutils.get_from_json_by_string(details, 'jdPrice.op')
            sku_details['plus_price'] = eutils.get_from_json_by_string(details, 'jdPrice.tpp')

        sku_details.update({
            'availability': avail,
            'normalized_availability': web_utils.normalize_availability(avail),
            'harvested_area': eutils.get_from_json_by_string(details,
                                                             'area.provinceName') + eutils.get_from_json_by_string(
                details,
                'area.cityName') + eutils.get_from_json_by_string(
                details, 'area.townName', ''),
            'sub_store_name': eutils.get_from_json_by_string(details, 'D.vender') or eutils.get_from_json_by_string(
                details, 'self_D.vender'),
            'sub_store_url': web_utils.normalize_url(
                eutils.get_from_json_by_string(details, 'D.url') or eutils.get_from_json_by_string(details,
                                                                                                   'self_D.url'), ),
            'freight': eutils.get_from_json_by_string(details, 'eir.0.iconSrc')
        })
        return sku_details

    def scrape_desc(self, driver):
        desc = dict()

        desc['title'] = eutils.find_str(driver.get_source(), r'\s+name:\s*\'(.+?)\',\s*$')[0].encode('utf-8').decode(
            'unicode_escape')
        desc['product_image'], desc['secondary_images'] = self.get_primary_secondary_images(driver.get_source())
        desc['vender_id'] = eutils.find_str(driver.get_source(), r'\s+venderId:\s*(\d+?),')[0]
        desc['cat_ids'] = eutils.find_str(driver.get_source(), r'\s+cat:\s*\[([\d,]+?)\],')[0]
        desc['video_text'] = eutils.find_str(driver.get_source(), r'\s+imageAndVideoJson:\s*(\{.*?\})')
        return desc

    def scrape_dynamics(self, driver):
        dynamics = dict()
        dynamics.update(
            self.get_trasaction(driver, self.oneline['product_code'], '2_2813_51976_0', self.oneline['vender_id'],
                                self.oneline['cat_ids']))
        return dynamics

    def parse(self, driver, params):
        self.oneline = dict()
        self.oneline['product_code'] = super().get_product_code(r'(\d+)\.html', params['entry'])
        # Start static page source
        driver.open_url(params['entry'])

        # setup GEO info

        # Update basic & dynamics info
        self.oneline['param_url'] = params['entry']
        self.oneline.update(self.scrape_desc(driver))
        self.oneline.update(self.scrape_dynamics(driver))
        print(self.oneline)

        return self.oneline
