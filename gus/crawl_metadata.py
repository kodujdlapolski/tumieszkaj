import logging
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

from gus.crawlers import (
    MeasuresSpider,
    LevelsSpider,
    AttributesSpider,
    AggregatesSpider,
    AreasSpider,
    VariablesSpider,
    SubjectsSpider
)
from gus.crawlers import get_settings


def crawl_metadata():
    process = CrawlerProcess(settings=get_settings(), install_root_handler=True)
    process.crawl(MeasuresSpider)
    process.crawl(LevelsSpider)
    process.crawl(AttributesSpider)
    process.crawl(AggregatesSpider)
    process.crawl(AreasSpider)
    process.crawl(VariablesSpider)
    process.crawl(SubjectsSpider)
    process.start()


if __name__ == '__main__':
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        # FIXME For some reason files with .log extension are not shown im Intellij
        filename='log-{:%Y-%m-%d-%H-%M-%S}.txt'.format(datetime.now()),
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG
    )

    crawl_metadata()
