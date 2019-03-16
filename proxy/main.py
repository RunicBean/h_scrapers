import requests
from lxml import etree

import template


HEADERS = {
    'referer': 'https://www.xicidaili.com/wn/',
    'host': 'www.xicidaili.com',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
}


def get_content(url):
    response = requests.get(url, headers=HEADERS)
    ip_ports = []
    t = template.extract_value(response.text, '//table[@id="ip_list"]/tr[@class]/td[position()>1 and position() < 4]', 'text')
    tlist = t.split('|')
    for t in tlist:
        if (tlist.index(t) + 1) % 2 == 0:
            pair.append(t)
            ip_ports.append(':'.join(pair))
        else:
            pair = []
            pair.append(t)
    return ip_ports


def proxy_validation(proxy):
    try:
        response = requests.get('http://www.baidu.com', proxies=proxy, timeout=1.5)
    except:
        return False
    return True if response.status_code == 200 else False


if __name__ == '__main__':
    print(get_content('https://www.xicidaili.com/nt/'))
    for ip_port in get_content('https://www.xicidaili.com/nt/'):
        proxy = {'http': 'http://{}'.format(ip_port),
                 'https': 'https://{}'.format(ip_port)}
        if proxy_validation(proxy):
            print('{} Connected Success!'.format(ip_port))
        else:
            print('{} Failed'.format(ip_port))
