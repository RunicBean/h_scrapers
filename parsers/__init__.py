import re
import abc

import core.ref_utils as cru
from errors import InputError


def select(store, type):
    pr_mod = __import__(__name__)
    d = dir(pr_mod)

    pr_mods = cru.load_modules(pr_mod)
    for m in pr_mods:
        parser = m.Parser()
        x = parser.store
        if parser.store == store and parser.type == type:
            return parser


class BaseProductParser(metaclass=abc.ABCMeta):

    @staticmethod
    def get_product_code(pattern, url):
        product_code = re.findall(pattern, url)[0] if len(re.findall(pattern, url)) > 0 else ''
        if not product_code:
            raise InputError('Given URL contains invalid product code. Please retry.')
        return product_code

    def parse(self, driver, params):
        pass

    @abc.abstractmethod
    def scrape_desc(self, driver):
        pass

    @abc.abstractmethod
    def scrape_dynamics(self, driver):
        pass


class BaseSearchParser(metaclass=abc.ABCMeta):

    def parse(self, driver, params):
        pass

    def param_validate(self, param):
        for necess_column in ['search_term', 'store']:
            if necess_column not in param:
                raise KeyError('Expected column lost: {}'.format(necess_column))
