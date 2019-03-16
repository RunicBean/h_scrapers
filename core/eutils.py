import re
import math


def to_float(num, ndigits=None, none_value=None, method=round):
    try:
        fnum = float(num)
        if method == round:
            return method(fnum, ndigits) if ndigits >= 0 else fnum
        elif method == math.floor or method == math.ceil:
            return method(fnum)
    except:
        return none_value or None


def get_from_json_by_string(json_obj, string, default=None):

    def getSubJson(json_obj, sep):
        if isinstance(json_obj, list):
            return json_obj[int(sep)] if len(json_obj) > int(sep) else None
        elif isinstance(json_obj, dict):
            return json_obj.get(sep)
        else:
            raise TypeError('Not valid data type when get_from_json_by_string: Expected(list/dict) Provided({})'.format(type(json_obj)))

    # sep_list = string.split('.')
    dot_match = re.findall(r'(.+?)\.', string)
    if dot_match:
        new_json_obj = getSubJson(json_obj, dot_match[0])
        if not new_json_obj:
            return default
        string = string.replace(dot_match[0] + '.', '', 1)
        return get_from_json_by_string(new_json_obj, string, default)
    else:
        return getSubJson(json_obj, string) if getSubJson(json_obj, string) else default


def strip(string_or_list):
    if type(string_or_list) in [str, bytes]:
        return string_or_list.strip()
    elif type(string_or_list) is list:
        return [strip(a) for a in string_or_list]
    elif type(string_or_list) is dict:
        for k, v in string_or_list.items():
            string_or_list[k] = strip(v)
        return string_or_list
    else:
        return string_or_list


def extract_numbers(text):
    if text:
        a = re.findall(r'[\d,]*[\.\d]+', text)
        if a:
            return a[0].replace(',', '')
        else:
            return ''
    return text


def find_str(my_str, regexp, ignore_case=True):
    if not my_str:
        return []
    elif type(my_str) not in [bytes, str]:
        my_str = str(my_str)

    if ignore_case:
        groups = re.findall(regexp, my_str, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    else:
        groups = re.findall(regexp, my_str, re.MULTILINE | re.DOTALL)
    return groups if groups else []


def remove(my_str, exprs):
    new_str = my_str
    if type(exprs) is list:
        for expr in exprs:
            new_str = remove(new_str, expr)
        return new_str
    elif type(exprs) in [str, bytes]:
        return re.sub(exprs, '', my_str)
    else:
        raise Exception('Type {} is not suppored'.format(type(exprs)))
