import re
import json

from lxml import etree

from core import eutils
from core import web_utils


def get_element_text(element, delimeter='|', convert_to_number=False):
    if element is None:
        return ''

    if isinstance(element, str):
        value = eutils.strip(element)
    else:
        value = delimeter.join([v for v in eutils.strip(list(element.itertext())) if v]) \
                or eutils.strip(element.text) \
                or eutils.strip(element.tail)
    if convert_to_number:
        return eutils.extract_numbers(value)
    else:
        return eutils.strip(value)


def extract_value(html, xpath_expr, value_method):
    if not xpath_expr:
        return value_method

    if type(html) in [str]:
        if value_method.startswith('dirregex:'):
            re_expr = value_method.replace('dirregex:', '')
            pattern = re.compile(re_expr, re.S)
            re_match = pattern.findall(html) if html else None
            if re_match:
                return re_match[0]
        if value_method.startswith('regexjson:'):
            if '|' not in value_method:
                raise Exception('Invalid expression: {}'.format(value_method))
            re_expr = value_method.replace('regexjson:', '').split('|')[0]
            json_expr = value_method.replace('regexjson:', '').split('|')[1]
            pattern = re.compile(re_expr, re.S)
            re_match = pattern.findall(html) if html else None
            if re_match:
                json_text = re_match[0].replace('\n', '').replace(' ', '')
                json_obj = json.loads(json_text)
                matched_text = eutils.get_from_json_by_string(json_obj, json_expr, '')
                if matched_text:
                    return matched_text
        html_element = etree.HTML(html)
    else:
        html_element = html

    elms = html_element.xpath(xpath_expr)  # only the first match is returned

    # Element found: get value
    values = []
    for elm in elms:
        value = None
        if value_method == 'text':
            value = get_element_text(elm)
        elif value_method == 'ptext':
            value = get_element_text(elm, delimeter='')
        elif value_method == 'number':
            value = get_element_text(elm, delimeter='', convert_to_number=True)
        elif value_method == 'url':
            value = get_element_text(elm, delimeter='')
            value = web_utils.normalize_url(value)
        elif value_method.startswith('re:'):
            re_expr = value_method.replace('re:', '')
            text_value = get_element_text(elm)
            re_match = re.findall(re_expr, text_value.replace('|', '')) if text_value else None
            if re_match:
                value = re_match[0]
        elif value_method.startswith('value:'):
            value = value_method.split(':')[1]
        elif value_method.startswith('attrs:'):
            attr_names = value_method.split(':')[1].split('|')
            for attr in attr_names:
                if elm.attrib.get(attr):
                    value = elm.attrib.get(attr)
                    break
        else:
            raise Exception('Expression not recognized: {}'.format(value_method))

        if eutils.strip(value):
            values.append(eutils.strip(value))

    return '|'.join([v for v in values if eutils.strip(v)]) if values else None


def parse_elements_xpath(html, element_definitions, raise_exception=False):

    result_dict = {}
    for dict_key, mandatory, value_extractions in element_definitions:

        # bcss_expr, value_method
        value = None
        for xpath_expr, value_method in value_extractions:
            value = extract_value(html, xpath_expr, value_method)
            if value:
                print(u'Element matched: {}: {}'.format(dict_key, value))
                result_dict[dict_key] = value
                break

        if value:
            continue
        elif mandatory:
            print('Mandatory element not found: {}'.format(dict_key))
            print('Template matching aborted.')
            return None
        else:
            result_dict[dict_key] = ''
            continue

    print('Template matching completed.')
    return result_dict


def parse_html(html_source, xpath_expr):
    return etree.HTML(html_source).xpath(xpath_expr)
