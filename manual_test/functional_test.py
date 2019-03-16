import unittest

import core.driver as cdr
import parsers as prs
import config


class TestInitiation(unittest.TestCase):

    def test_scrape_jd_details(self):
        self.params = {
            'store': 'jd',
            'type': 'details',
            'entry': 'https://item.jd.com/6930866.html',
        }

        self.driver = cdr.Driver()

        self.parser = prs.select(self.params['store'], self.params['type'])

        self.assertEqual(self.parser.store, 'jd')
        self.assertEqual(self.parser.type, 'details')
        oneline = self.parser.parse(self.driver, self.params)[0]
        self.assertEqual(oneline['title'], '奥妙 洗衣液 18.3斤超值 除菌除螨 大礼包 源自天然酵素(新老包装随机发货)')
        # self.assertEqual(oneline['product_code'], '7730877')

    def test_config_file_load_correctly(self):
        cc = config.configure()
        self.assertEqual(cc.get('file_path', 'data_path'), '/Users/yuxhuang/Documents/GitHub/h_scrapers/data')

    def test_scrape_jd_category_search(self):
        self.params = {
            'store': 'jd',
            'type': 'search',
            'search_term': '卫生纸',
            'geo': 'Shanghai',
            'limit': 150
        }

        self.driver = cdr.Driver()
        self.parser = prs.select(self.params['store'], self.params['type'])

        self.assertEqual(self.parser.store, 'jd')
        self.assertEqual(self.parser.type, 'search')
        search_results = self.parser.parse(self.driver, self.params)
        # self.assertIn(1, search_results[0])


if __name__ == '__main__':
    unittest.main(verbosity=1)
