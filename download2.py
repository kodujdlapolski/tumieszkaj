import os

from gus_crawler import Crawler

crawler = Crawler()

request_fname = 'ilosc_terenow_zielonych_gmina.json'
request_fpath = f'requests/{request_fname}'
parent_unit_id = crawler.units_api.units_search_get(name='Imielin').results[
    0].parent_id
parent_unit_name = crawler.units_api.units_by_id_get(parent_unit_id).name
units = crawler.units_api.units_get(parent_id=parent_unit_id,
                                    page_size=crawler.MAX_PAGE_SIZE).results

units = [unit.name for unit in units]
units.append(parent_unit_name)
units.append('DOLNOŚLĄSKIE')

request = crawler.import_request(request_fpath)
for unit_name in units:
    df = crawler.download(request, unit_name)
    dir = f'data/{unit_name}'
    if not os.path.exists(dir):
        os.makedirs(dir)
    fpath = f'{dir}/{request_fname}.csv'
    df.to_csv(fpath, index=True)
