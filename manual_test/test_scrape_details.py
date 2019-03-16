import csv
import os

import core.driver as cdr
import parsers as prs
import config
from parsers._constant import SEARTH_COLUMNS

if __name__ == '__main__':
    cc = config.configure()
    param_list = []
    with open(os.path.join(cc.get('file_path', 'data_path'), 'seed.csv')) as csv_r:
        csf = csv.reader(csv_r)
        for cs in csf:
            param_list.append(cs)

    for row in param_list[1:]:
        params = {
            'store': row[0],
            'type': row[1],
            'search_term': row[2],
            'geo': row[3],
            'limit': row[4]
        }

        driver = cdr.Driver()
        parser = prs.select(params['store'], params['type'])
        rows = parser.parse(driver, params)
        new_rows = []
        for row in rows:
            new_rows.append([row.get(h) for h in SEARTH_COLUMNS])
        with open(os.path.join(cc.get('file_path', 'data_path'), 'feed.csv'), 'a') as csv_w:
            csv_writer = csv.writer(csv_w)
            csv_writer.writerows(new_rows)


