from anytree.importer import JsonImporter

from gus_crawler import Crawler

crawler = Crawler()
importer = JsonImporter()

l = [
    (
        [   'nieruchomosci_gmina.json',
            'ilosc_terenow_zielonych_gmina.json',
            'sport_gmina.json'
        ],
        ['Imielin']),

    (['nieruchomosci_powiat.json'], ['Powiat bieruńsko-lędziński'])
]

for requests_fnames, units in l:
    for request_fname in requests_fnames:
        request_fpath = f'requests/{request_fname}'
        request = crawler.import_request(request_fpath)
        crawler.print_download_request(request)
        for unit_name in units:
            df = crawler.download(request, unit_name)
            fpath = f'data/{unit_name}/{request_fname}.csv'
            df.to_csv(fpath, index=True)
