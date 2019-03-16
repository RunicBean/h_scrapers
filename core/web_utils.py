import re

from core import eutils


def normalize_url(url):
    if url.startswith('//'):
        return 'https:' + url
    elif not url.startswith('http'):
        return 'http://' + url


def normalize_availability(avail_text):
    if not avail_text:
        return ''

    mappings = {
        'In stock': [u'in stock',u'通常.*?发货', u'In stock', u'^库存\d+件$', u'有货', u'现货', u'限购\d+件', u'预订', u'立即购买', u'即将开始',
                     u'[放加]入购物[车袋]', u'充足', u'立即抢购', u'仅剩', u'支付定金', u'可配货',  u'通常需要.+发货',
                     u'구매하기', u'장바구니 담기', u'바로구매', u'instock', u'采购中', u'장바구니 담기', u'现在可订购'],

        'Out of stock': [u'현재 구매가 불가능한 상품입니다.',u'out of stock online', u'Out of stock', u'无货', u'缺货', u'还有机会', u'卖光了', u'售罄', u'抢光', u'不足', u'到货通知',
                         u'soldout', u'일시품절', u'Out of Stock', u'매진', u'재입고 준비중', u'품절'],

        'Void': [u'^Void$', u'下架', u'Off Shelf', u'不能购买', u'下柜', u'结束', u'不支持在当前.+销售',
                 u'暂不支持销售', u'판매 종료', u'暂不销售', u'现在从']
    }
    for value, exprs in mappings.items():
        for expr in exprs:
            if re.findall(expr, avail_text):
                return value

    return 'Undefined'


if __name__ == '__main__':
    test_json = [
        {'ertg': 346},
        [
            {2435: 'aerg'},
            {'aseg': 'ag'}
        ]
    ]
    ret = eutils.get_from_json_by_string(test_json, '1.0.2435', None)
    print(ret)
    print(type(ret))
