import json

import scrapy
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.http.request import Request
# TODO I would like to particular order of fields in export, because now it
#      sometimes changes: https://stackoverflow.com/questions/10844064/items-in-json-object-are-out-of-order-using-json-dumps
# TODO How do we to make sure we have *all* GUS metadata?
# TODO Should I use item loaders for Scrapy?
# TODO Make sure Retry-After is respected
#      This is not implemented yet in Scrapy: https://github.com/scrapy/scrapy/issues/3849
from scrapy.utils.response import response_status_message


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
    # TODO This should go to crawler.settings
    data_dir = 'data'


class PagedSpider(GusSpider):
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
    name = 'gus_subjects'
    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': f'{GusSpider.data_dir}/subjects.jl'}

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
    name = 'gus_areas'
    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': f'{GusSpider.data_dir}/areas.jl'}

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
    name = 'gus_levels'
    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': f'{GusSpider.data_dir}/levels.jl'}

    def start_requests(self):
        url = f'{self.base_url}/levels?lang=pl&format=json&page-size={self.MAX_PAGE_SIZE}'
        yield Request(url, self.parse)

    def handle_result(self, result, response_body):
        level = Level()
        level['id'] = result['id']
        level['name'] = result['name']
        yield level


class AttributesSpider(PagedSpider):
    name = 'gus_attributes'
    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': f'{GusSpider.data_dir}/attributes.jl'}

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
    name = 'gus_aggregates'
    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': f'{GusSpider.data_dir}/aggregates.jl'}

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
    name = 'gus_measures'

    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': f'{GusSpider.data_dir}/measures.jl'}

    def start_requests(self):
        url = f'{self.base_url}/measures?lang=pl&format=json&page-size={self.MAX_PAGE_SIZE}'
        yield Request(url, self.parse)

    def handle_result(self, result, response_body):
        measure = Measure()
        measure['id'] = result['id']
        measure['name'] = result['name']
        yield measure


class VariablesSpider(PagedSpider):
    name = 'gus_variables'

    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': f'{GusSpider.data_dir}/variables.jl'}

    def start_requests(self):
        url = f'{self.base_url}/variables?lang=pl&format=json&page-size={self.MAX_PAGE_SIZE}'
        yield Request(url, self.parse)

    def _parse_var_name(self, body):
        return ' '.join([body[field]
                         for field
                         in ['n1', 'n2', 'n3', 'n4', 'n5']
                         if field in body])

    def handle_result(self, result, response_body):
        var = Variable()
        var['id'] = result['id']
        var['name'] = self._parse_var_name(result, response_body)
        var['level'] = result['level']
        var['measureId'] = result['measureUnitId']
        var['subjectId'] = result['subjectId']
        yield var


class DataSpider(PagedSpider):
    name = 'gus_data'

    custom_settings = {'FEED_FORMAT': 'jsonlines',
                       'FEED_URI': f'{GusSpider.data_dir}/data.jl'}

    def is_localility(self, area_id):
        # Statistical towns level, i.e, level = 7
        return '-' in area_id

    def start_requests(self):
        for area_id in self.areas_ids:
            query = '&'.join(f'var-id={var_id}' for var_id in self.vars_ids)
            if self.is_localility(area_id):
                url = f'{self.base_url}/data/localities/by-unit/{area_id}/?lang=pl&format=json&{query}&page-size={self.MAX_PAGE_SIZE}'
            else:
                url = f'{self.base_url}/data/by-unit/{area_id}/?lang=pl&format=json&{query}&page-size={self.MAX_PAGE_SIZE}'
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


class ApiKeyAuthMiddleware(object):
    """Set X-ClientId Authorization header
    (api_key spider class attribute)"""

    @classmethod
    def from_crawler(cls, crawler):
        o = cls()
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        self.api_key = spider.crawler.settings.get('API_KEY')
        if self.api_key is None:
            raise ValueError('API_KEY not set')

    def process_request(self, request, spider):
        request.headers[b'X-ClientId'] = self.api_key


class FailedStatsMiddleware(object):
    # TODO Ask for feedback on GitHub

    def __init__(self, stats):
        self.stats = stats

    EXCEPTIONS_TO_FAIL = RetryMiddleware.EXCEPTIONS_TO_RETRY

    def __init__(self, settings):
        self.failure_http_codes = set(range(400, 600))

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def process_response(self, request, response, spider):
        if response.status in self.failure_http_codes:
            reason = response_status_message(response.status)
            return self._fail(request, reason, spider) or response

        successful_url = request.url
        spider.failed_urls.discard(successful_url)

        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_FAIL):
            return self._fail(request, exception, spider)

    def _fail(self, request, reason, spider):
        spider.failed_urls.add(request.url)

    def spider_opened(self, spider):
        spider.failed_urls = set()

    def spider_closed(self, spider):
        stats = spider.crawler.stats
        stats.set_value('failed_urls', ','.join(spider.failed_urls))


def get_settings():
    return {
        'CONCURRENT_REQUESTS': 16,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': True,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {'gus.crawlers.ApiKeyAuthMiddleware': 543,
                                   'gus.crawlers.FailedStatsMiddleware': 950},
        'API_KEY': 'afeb163d-fab0-48e0-eb76-08d75c76efda',
        'DOWNLOADER_STATS': True,

    }
