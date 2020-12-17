# TuMieszkaj

Repozytorium zawiera wszystkie narzędzia do pracy z danymi dla aplikacji [TuMieszkaj](https://kodujdlapolski.pl/projects/tumieszkaj/).

## Instalacja

Aby zainstalować wszystkie narzędzia wymagana jest [Anaconda](https://www.anaconda.com/).

Następnie należy wykonać następujące instrukcje w konsoli:

```$bash
git clone https://github.com/kodujdlapolski/tumieszkaj.git
cd tumieszkaj
conda env create --file environment.yml
conda activate tumieszkaj
```

Po uruchomieniu zainstalowane są wszystkie wymagane zależności.

## Robot dla Bazy Danych Lokalnych GUS

Robot (crawler, spider) pozwala na ściągania z Bazy Danych Lokalnych GUS zarówno metadanych (lista wszystkich 
zmiennych, ich kategorii, jednostek terytorialnych i statystycznych z GUSu, itp.) jak i samych 
wartości zmiennych.

### Sposób użycia

Aby ściągnąć wszystkie metadane należy uruchomić:

```$bash
pip install -e .
python scripts/crawl_gus_bdl_metadata.py --api-key "afeb163d-..." --feed-dir "data/gus/metadata"
```

Aby ściągnąć wybrane dane dla województwa dolnośląskiego należy uruchomić: 

```$bash
pip install -e .
python scripts/crawl_dolnoslaskie_data.py --api-key "afeb163d-..." --feed-dir "data/gus/data" 
  --metadata-dir "data/gus/metadata"
```

Lista zmiennych i obszar, dla których chcemy ściągnąć dane jest określony w pliku `crawl_data.py`.

## Lokalna instancja OpenStreetMap dla wybranego województwa

Aby uruchomić lokalną instancję OpenStreetMap (OSM) dla wybranego województwa 
(tutaj śląskiego), wymagane jest środowisko z Dockerem. Następnie należy zainicjalizować 
kontener dockera:

```bash
docker run \
  -e OVERPASS_META=yes \
  -e OVERPASS_MODE=init \
  -e OVERPASS_PLANET_URL=http://download.geofabrik.de/europe/poland/slaskie-latest.osm.bz2 \
  -e OVERPASS_DIFF_URL=http://download.geofabrik.de/europe/poland/slaskie-updates/ \
  -e OVERPASS_RULES_LOAD=10 \
  -v /big/docker/overpass_db/:/db \
  -p 12345:80 \
  -i -t \
  --name overpass_slaskie wiktorn/overpass-api
```

Uruchomienia kontenera:

```bash
docker start overpass_slaskie
```

Overpass API dla tak postawionej instancji OSM jest teraz dostępny pod: 
[http://localhost:12345/api/interpreter](http://localhost:12345/api/interpreter).

### Architektura

Robot korzysta z [API RESTowego](https://api.stat.gov.pl/Home/BdlApi) wystawionego przez GUS. 
Crawler używa biblioteki [Scrapy](https://scrapy.org/) do zarządzania ruchem, tj. ilością zapytań na 
minutę, ponieważ GUS narzuca określony [Rate Limiting](https://en.wikipedia.org/wiki/Rate_limiting), 
czyli dopuszczalną ilość zapytań na minutę, miesiąc, etc.

## Lokalna instancja OpenStreetMap dla wybranego województwa

Aby uruchomić lokalną instancję OpenStreetMap (OSM) dla wybranego województwa 
(tutaj śląskiego), wymagane jest środowisko z Dockerem. Następnie należy zainicjalizować 
kontener dockera:

```bash
docker run \
  -e OVERPASS_META=yes \
  -e OVERPASS_MODE=init \
  -e OVERPASS_PLANET_URL=http://download.geofabrik.de/europe/poland/slaskie-latest.osm.bz2 \
  -e OVERPASS_DIFF_URL=http://download.geofabrik.de/europe/poland/slaskie-updates/ \
  -e OVERPASS_RULES_LOAD=10 \
  -v /big/docker/overpass_db/:/db \
  -p 12345:80 \
  -i -t \
  --name overpass_slaskie wiktorn/overpass-api
```

Uruchomienia kontenera:

```bash
docker start overpass_slaskie
```

Overpass API dla tak postawionej instancji OSM jest teraz dostępny pod: 
[http://localhost:12345/api/interpreter](http://localhost:12345/api/interpreter).

## Overpass API client

TBD

## Nominatim API client

TBD


### Licencje

#### Oprogramowanie

MIT License.

#### Dane GUS

Dane Głównego Urzędu Statystycznego (GUS) pochodzą ze [Bazy Danych Lokalnych](https://bdl.stat.gov.pl/BDL).
Główny Urząd Statystyczny nie ma zastrzeżeń co do kopiowania plików i stron oraz dokonywania 
wydruków, w tym do własnych opracowań, pod warunkiem, że będzie podane ich źródło. Szczegółowe
informacje na temat praw autorskich tych danych znajdują się na na [stronie GUSu](https://stat.gov.pl/copyright).


