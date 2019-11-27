from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message


class ApiKeyAuthMiddleware:
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


class FailedStatsMiddleware:
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
