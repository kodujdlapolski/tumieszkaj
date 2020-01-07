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

Aby ściągnąć wybrane dane dla LGOnależy uruchomić: 

```$bash
pip install -e .
python scripts/crawl_dolnoslaskie_data.py --api-key "afeb163d-..." --feed-dir "data/gus/data" 
  --metadata-dir "data/gus/metadata"
```

Lista zmiennych i obszar, dla których chcemy ściągnąć dane jest określony w pliku `crawl_data.py`.

### Architektura

Robot korzysta z [API RESTowego](https://api.stat.gov.pl/Home/BdlApi) wystawionego przez GUS. 
Crawler używa biblioteki [Scrapy](https://scrapy.org/) do zarządzania ruchem, tj. ilością zapytań na 
minutę, ponieważ GUS narzuca określony [Rate Limiting](https://en.wikipedia.org/wiki/Rate_limiting), 
czyli dopuszczalną ilość zapytań na minutę, miesiąc, etc.

### Licencje

#### Oprogramowanie

MIT License.

#### Dane GUS

Dane Głównego Urzędu Statystycznego (GUS) pochodzą ze [Bazy Danych Lokalnych](https://bdl.stat.gov.pl/BDL).
Główny Urząd Statystyczny nie ma zastrzeżeń co do kopiowania plików i stron oraz dokonywania 
wydruków, w tym do własnych opracowań, pod warunkiem, że będzie podane ich źródło. Szczegółowe
informacje na temat praw autorskich tych danych znajdują się na na [stronie GUSu](https://stat.gov.pl/copyright).


