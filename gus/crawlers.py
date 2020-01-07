"""
The Scrapy crawlers for crawling data and metadata from GUS BDL API.
"""

import json

import scrapy
from scrapy.http.request import Request


# TODO I would like to particular order of fields in export, because now it
#      sometimes changes: https://stackoverflow.com/questions/10844064/items-in-json-object-are-out-of-order-using-json-dumps
# TODO How do we to make sure we have *all* GUS metadata?
# TODO Should I use item loaders for Scrapy?
# TODO Make sure Retry-After is respected
#      This is not implemented yet in Scrapy: https://github.com/scrapy/scrapy/issues/3849


class Variable(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    level = scrapy.Field()
    measureId = scrapy.Field()
    measureUnitName = scrapy.Field()
    subjectId = scrapy.Field()


class Attribute(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    symbol = scrapy.Field()
    description = scrapy.Field()


class Aggregate(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    level = scrapy.Field()
    description = scrapy.Field()


class Subject(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    parentId = scrapy.Field()
    description = scrapy.Field()


class Area(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    parentId = scrapy.Field()
    level = scrapy.Field()
    kind = scrapy.Field()


class Level(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()


class Measure(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()


class Datum(scrapy.Item):
    # TODO Perhaps more compact way would be better: https://bdl.stat.gov.pl/api/v1/data/by-unit/012415114021?var-id=10693&var-id=804&format=json
    #      See https://stackoverflow.com/questions/43396753/how-to-populate-a-scrapy-field-as-a-dictionary/43426675
    #      on how to use dictionaries in Scrapy items
    areaId = scrapy.Field()
    aggregateId = scrapy.Field()
    variableId = scrapy.Field()
    lastUpdate = scrapy.Field()
    year = scrapy.Field()
    value = scrapy.Field()
    attributeId = scrapy.Field()


class GusSpider(scrapy.Spider):
    allowed_domain = 'bdl.stat.gov.pl'
    base_url = 'https://bdl.stat.gov.pl/api/v1'


class PagedSpider(GusSpider):
    """
    Abstract spider to handle paged results.
    """

    MAX_PAGE_SIZE = 100

    def parse(self, response):
        body = json.loads(response.body_as_unicode())

        if 'links' in body and 'next' in body['links']:
            url = body['links']['next']
            yield Request(url, self.parse)

        for result in body['results']:
            yield from self.handle_result(result, body)

    def handle_result(self, result, response_body):
        raise NotImplementedError


class SubjectsSpider(PagedSpider):
    """
    Crawles metadata about available variable subjects.

    Construction parameters:

    feed_dir: directory where crawled metadata will be stored.
    """

    name = 'gus_subjects'
    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': '%(feed_dir)s/subjects.jl'}

    def __init__(self, *args, **kwargs):
        self.feed_dir = kwargs.pop('feed_dir', '')
        super(SubjectsSpider, self).__init__(*args, **kwargs)

    def subject_request(self, subject_id):
        url = f'{self.base_url}/subjects/{subject_id}?format=json&lang=pl'
        return Request(url, self.parse_subject)

    def start_requests(self):
        url = f'{self.base_url}/subjects?lang=pl&format=json&page-size={self.MAX_PAGE_SIZE}'
        yield Request(url, self.parse)

    def handle_result(self, result, response_body):

        subject_id = result['id']
        yield self.subject_request(subject_id)

        if 'children' in result:
            children = result['children']
            for subject_id in children:
                yield self.subject_request(subject_id)

    def parse_subject(self, response):
        body = json.loads(response.body_as_unicode())

        if 'children' in body:
            children = body['children']
            for subject_id in children:
                yield self.subject_request(subject_id)

        subject = Subject()
        subject['id'] = body['id']
        subject['name'] = body['name']
        if 'parentId' in body:
            subject['parentId'] = body['parentId']
        if 'description' in body:
            subject['description'] = body['description']

        yield subject


class AreasSpider(PagedSpider):
    """
    Crawles metadata about available areas.

    Construction parameters:

    feed_dir: directory where crawled metadata will be stored.
    """

    name = 'gus_areas'
    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': '%(feed_dir)s/areas.jl'}

    def __init__(self, *args, **kwargs):
        self.feed_dir = kwargs.pop('feed_dir', '')
        super(AreasSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        url = f'{self.base_url}/units?lang=pl&format=json&page-size={self.MAX_PAGE_SIZE}'
        yield Request(url, self.parse)

    def handle_result(self, result, response_body):

        level = result['level']
        if level == 6:
            id = result['id']
            url = f'{self.base_url}/units/localities?parent-id={id}' \
                  f'&lang=pl&format=json&page-size={self.MAX_PAGE_SIZE}'
            yield Request(url, self.parse)

        area = Area()
        area['id'] = result['id']
        area['name'] = result['name']
        area['level'] = result['level']
        if 'kind' in result:
            area['kind'] = result['kind']
        if 'parentId' in result:
            area['parentId'] = result['parentId']
        yield area


class LevelsSpider(PagedSpider):
    """
    Crawles metadata about available levels.

    Construction parameters:

    feed_dir: directory where crawled metadata will be stored.
    """

    name = 'gus_levels'
    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': '%(feed_dir)s/levels.jl'}

    def __init__(self, *args, **kwargs):
        self.feed_dir = kwargs.pop('feed_dir', '')
        super(LevelsSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        url = f'{self.base_url}/levels?lang=pl&format=json&page-size={self.MAX_PAGE_SIZE}'
        yield Request(url, self.parse)

    def handle_result(self, result, response_body):
        level = Level()
        level['id'] = result['id']
        level['name'] = result['name']
        yield level


class AttributesSpider(PagedSpider):
    """
    Crawles metadata about available attributes.

    Construction parameters:

    feed_dir: directory where crawled metadata will be stored.
    """

    name = 'gus_attributes'
    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': '%(feed_dir)s/attributes.jl'}

    def __init__(self, *args, **kwargs):
        self.feed_dir = kwargs.pop('feed_dir', '')
        super(AttributesSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        url = f'{self.base_url}/attributes?lang=pl&format=json&page-size={self.MAX_PAGE_SIZE}'
        yield Request(url, self.parse)

    def handle_result(self, result, response_body):
        attribute = Attribute()
        attribute['id'] = result['id']
        attribute['name'] = result['name']
        attribute['symbol'] = result['symbol']
        attribute['description'] = result.get('description', None)
        yield attribute


class AggregatesSpider(PagedSpider):
    """
    Crawles metadata about available aggregates.

    Construction parameters:

    feed_dir: directory where crawled metadata will be stored.
    """

    name = 'gus_aggregates'
    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': '%(feed_dir)s/aggregates.jl'}

    def __init__(self, *args, **kwargs):
        self.feed_dir = kwargs.pop('feed_dir', '')
        super(AggregatesSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        url = f'{self.base_url}/aggregates?lang=pl&format=json&page-size={self.MAX_PAGE_SIZE}'
        yield Request(url, self.parse)

    def handle_result(self, result, response_body):
        aggregate = Aggregate()
        aggregate['id'] = result['id']
        aggregate['name'] = result['name']
        aggregate['level'] = result['level']
        aggregate['description'] = result.get('description', None)
        yield aggregate


class MeasuresSpider(PagedSpider):
    """
    Crawles metadata about available measures.

    Construction parameters:

    feed_dir: directory where crawled metadata will be stored.
    """


name = 'gus_measures'

custom_settings = {'FEED_FORMAT': 'jsonlines',
                   'FEED_URI': '%(feed_dir)s/measures.jl'}


def __init__(self, *args, **kwargs):
    self.feed_dir = kwargs.pop('feed_dir', '')
    super(MeasuresSpider, self).__init__(*args, **kwargs)


def start_requests(self):
    url = f'{self.base_url}/measures?lang=pl&format=json' \
          f'&page-size={self.MAX_PAGE_SIZE}'
    yield Request(url, self.parse)


def handle_result(self, result, response_body):
    measure = Measure()
    measure['id'] = result['id']
    measure['name'] = result['name']
    yield measure


class VariablesSpider(PagedSpider):
    """
    Crawles metadata about available variables.

    Construction parameters:

    feed_dir: directory where crawled metadata will be stored.
    """

    name = 'gus_variables'

    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': '%(feed_dir)s/variables.jl'}

    def __init__(self, *args, **kwargs):
        self.feed_dir = kwargs.pop('feed_dir', '')
        super(VariablesSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        url = f'{self.base_url}/variables?lang=pl&format=json' \
              f'&page-size={self.MAX_PAGE_SIZE}'
        yield Request(url, self.parse)

    def _parse_var_name(self, body):
        return ' '.join([body[field]
                         for field
                         in ['n1', 'n2', 'n3', 'n4', 'n5']
                         if field in body])

    def handle_result(self, result, response_body):
        var = Variable()
        var['id'] = result['id']
        var['name'] = self._parse_var_name(result)
        var['level'] = result['level']
        var['measureId'] = result['measureUnitId']
        var['subjectId'] = result['subjectId']
        yield var


class DataSpider(PagedSpider):
    """
    Crawles data for all years for variables and areas given when constructing
    a crawler.

    Construction parameters:

     vars_ids: IDs of variables to crawl.
    areas_ids: IDs of areas to crawl.
     feed_dir: directory where crawled data will be stored.
    """

    name = 'gus_data'

    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': '%(feed_dir)s/data.jl'}

    def __init__(self, *args, **kwargs):
        self.feed_dir = kwargs.pop('feed_dir', '')
        super(DataSpider, self).__init__(*args, **kwargs)

    def is_localility(self, area_id):
        # Statistical towns level, i.e, level = 7
        return '-' in area_id

    def start_requests(self):
        for area_id in self.areas_ids:
            query = '&'.join(f'var-id={var_id}' for var_id in self.vars_ids)
            if self.is_localility(area_id):
                url = f'{self.base_url}/data/localities/by-unit/{area_id}/' \
                      f'?lang=pl&format=json&{query}&page-size={self.MAX_PAGE_SIZE}'
            else:
                url = f'{self.base_url}/data/by-unit/{area_id}/?lang=pl' \
                      f'&format=json&{query}&page-size={self.MAX_PAGE_SIZE}'
            yield Request(url, self.parse)

    def handle_result(self, result, response_body):
        for value in result['values']:
            datum = Datum()
            datum['areaId'] = response_body['unitId']
            datum['aggregateId'] = response_body['aggregateId']
            datum['variableId'] = result['id']
            datum['lastUpdate'] = result['lastUpdate']
            datum['year'] = value['year']
            datum['value'] = value['val']
            datum['attributeId'] = value['attrId']
            yield datum


def get_settings(api_key=None):
    settings = {
        'CONCURRENT_REQUESTS': 16,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': True,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {'gus.middleware.ApiKeyAuthMiddleware': 543,
                                   'gus.middleware.FailedStatsMiddleware': 950},
        'DOWNLOADER_STATS': True,
    }
    if not api_key is None:
        settings['API_KEY'] = api_key
    return settings
