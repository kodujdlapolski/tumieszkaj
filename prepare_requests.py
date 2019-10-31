from anytree.exporter import JsonExporter

from gus_crawler import Crawler



definitions = {
    'nieruchomosci_powiat.json': [
        'RYNEK NIERUCHOMOŚCI/RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH/Mediana cen za 1 m2 lokali mieszkalnych sprzedanych w ramach transakcji rynkowych/ogółem ogółem',
        'RYNEK NIERUCHOMOŚCI/RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH/Mediana cen za 1 m2 lokali mieszkalnych sprzedanych w ramach transakcji rynkowych/rynek pierwotny ogółem',
        'RYNEK NIERUCHOMOŚCI/RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH/Mediana cen za 1 m2 lokali mieszkalnych sprzedanych w ramach transakcji rynkowych/rynek wtórny ogółem',
        'RYNEK NIERUCHOMOŚCI/RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH/Średnia cena za 1 m2 lokali mieszkalnych sprzedanych w ramach transakcji rynkowych/ogółem ogółem',
        'RYNEK NIERUCHOMOŚCI/RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH/Średnia cena za 1 m2 lokali mieszkalnych sprzedanych w ramach transakcji rynkowych/rynek pierwotny ogółem',
        'RYNEK NIERUCHOMOŚCI/RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH/Średnia cena za 1 m2 lokali mieszkalnych sprzedanych w ramach transakcji rynkowych/rynek wtórny ogółem',
        'RYNEK NIERUCHOMOŚCI/RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH/Liczba lokali mieszkalnych sprzedanych w ramach transakcji rynkowych/ogółem ogółem',
        'RYNEK NIERUCHOMOŚCI/RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH/Liczba lokali mieszkalnych sprzedanych w ramach transakcji rynkowych/rynek pierwotny ogółem',
        'RYNEK NIERUCHOMOŚCI/RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH/Liczba lokali mieszkalnych sprzedanych w ramach transakcji rynkowych/rynek wtórny ogółem',
        'RYNEK NIERUCHOMOŚCI/RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH/Średnia cena lokali mieszkalnych sprzedanych w ramach transakcji rynkowych/ogółem ogółem',
        'RYNEK NIERUCHOMOŚCI/RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH/Średnia cena lokali mieszkalnych sprzedanych w ramach transakcji rynkowych/rynek pierwotny ogółem',
        'RYNEK NIERUCHOMOŚCI/RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH/Średnia cena lokali mieszkalnych sprzedanych w ramach transakcji rynkowych/rynek wtórny ogółem',
    ],
    'nieruchomosci_gmina.json': [
        'GOSPODARKA MIESZKANIOWA I KOMUNALNA/ZASOBY MIESZKANIOWE/Budynki mieszkalne w gminie/ogółem',
        'GOSPODARKA MIESZKANIOWA I KOMUNALNA/ZASOBY MIESZKANIOWE/Zasoby mieszkaniowe - wskaźniki/przeciętna powierzchnia użytkowa 1 mieszkania',
        'GOSPODARKA MIESZKANIOWA I KOMUNALNA/ZASOBY MIESZKANIOWE/Zasoby mieszkaniowe - wskaźniki/przeciętna powierzchnia użytkowa mieszkania na 1 osobę',
        'GOSPODARKA MIESZKANIOWA I KOMUNALNA/ZASOBY MIESZKANIOWE/Zasoby mieszkaniowe - wskaźniki/mieszkania na 1000 mieszkańców',
        'GOSPODARKA MIESZKANIOWA I KOMUNALNA/ZASOBY MIESZKANIOWE/Mieszkania niezamieszkane w zasobie gminy (pustostany)/ogółem'
    ],
    'ilosc_terenow_zielonych_gmina.json': [
        'STAN I OCHRONA ŚRODOWISKA/TERENY ZIELENI/Tereny zieleni - wskaźniki/udział parków, zieleńców i terenów zieleni osiedlowej w powierzchni ogółem',
        'STAN I OCHRONA ŚRODOWISKA/TERENY ZIELENI/Tereny zieleni/zieleńce obiekty ogółem (w miastach i na wsi)',
        'STAN I OCHRONA ŚRODOWISKA/TERENY ZIELENI/Tereny zieleni/zieleńce powierzchnia ogółem (w miastach i na wsi)',
        'STAN I OCHRONA ŚRODOWISKA/TERENY ZIELENI/Rodzinne ogrody działkowe/ogrody liczba',
        'STAN I OCHRONA ŚRODOWISKA/TERENY ZIELENI/Rodzinne ogrody działkowe/ogrody powierzchnia',
        'STAN I OCHRONA ŚRODOWISKA/TERENY ZIELENI/Rodzinne ogrody działkowe/działki liczba',
        'STAN I OCHRONA ŚRODOWISKA/TERENY ZIELENI/Rodzinne ogrody działkowe/działki powierzchnia',
        'STAN I OCHRONA ŚRODOWISKA/TERENY ZIELENI/Tereny zieleni/lasy gminne powierzchnia ogółem (w miastach i na wsi)',
        'STAN I OCHRONA ŚRODOWISKA/TERENY ZIELENI/Tereny zieleni/parki spacerowo - wypoczynkowe powierzchnia ogółem (w miastach i na wsi)',
    ],
    'sport_gmina.json': [
        'TRANSPORT I ŁĄCZNOŚĆ/ŚCIEŻKI ROWEROWE/Długość ścieżek rowerowych (dróg dla rowerów)/ścieżki rowerowe (drogi dla rowerów) ogółem',
        'KULTURA FIZYCZNA, SPORT I REKREACJA/SPORT/Kluby sportowe łącznie z klubami wyznaniowymi i UKS/kluby'
    ]
}


crawler = Crawler()
exporter = JsonExporter(indent=2)
for fname, paths in definitions.items():
    request = crawler.get_download_request(paths)
    crawler.print_download_request(request)
    with open(f'requests/{fname}', 'w') as f:
        exporter.write(request, f)
