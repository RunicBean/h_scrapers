import unittest

import core.driver as cdr
import parsers as prs
import config


class TestInitiation(unittest.TestCase):

    def test_driver_init_success(self):
        self.params = {
            'store': 'jd',
            'type': 'details',
            'entry': 'https://item.jd.com/7730877.html'
        }

        self.driver = cdr.Driver()

        self.parser = prs.select(self.params['store'], self.params['type'])

        self.assertEqual(self.parser.store, 'jd')
        self.assertEqual(self.parser.type, 'details')
        oneline = self.parser.parse(self.driver, self.params)
        self.assertEqual(oneline['title'], '开丽（Kaili）婴儿亲肤洗衣液宝宝儿童洗衣液1L装')

    def test_config_file_load_correctly(self):
        cc = config.configure()
        self.assertEqual(cc.get('file_path', 'data_path'), '/Users/yuxhuang/Documents/GitHub/h_scrapers/data')


if __name__ == '__main__':
    unittest.main(verbosity=1)
