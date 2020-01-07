import argparse
import logging
from datetime import datetime
from pathlib import Path

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


def crawl_metadata(api_key=None, feed_dir=None):
    """
    Runs a number of spiders to crawl GUS BDL metadata in parallel.

    :param api_key:
    :param feed_dir:
    """

    if feed_dir is None:
        raise ValueError('feed_dir is required')

    process = CrawlerProcess(settings=get_settings(api_key),
                             install_root_handler=True)
    process.crawl(MeasuresSpider, feed_dir=feed_dir)
    process.crawl(LevelsSpider, feed_dir=feed_dir)
    process.crawl(AttributesSpider, feed_dir=feed_dir)
    process.crawl(AggregatesSpider, feed_dir=feed_dir)
    process.crawl(AreasSpider, feed_dir=feed_dir)
    process.crawl(VariablesSpider, feed_dir=feed_dir)
    process.crawl(SubjectsSpider, feed_dir=feed_dir)
    process.start()


if __name__ == '__main__':
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        # FIXME For some reason files with .log extension are not shown im Intellij
        filename='log-{:%Y-%m-%d-%H-%M-%S}.txt'.format(datetime.now()),
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG
    )

    parser = argparse.ArgumentParser(description='Crawls metadata from GUS BDL')
    parser.add_argument('-k', '--api-key',
                        help='GUS BDL API key',
                        type=str,
                        required=True)
    parser.add_argument('-f', '--feed-dir',
                        help='Directory to store crawlers output',
                        type=str,
                        required=True)

    args = parser.parse_args()

    Path(args.feed_dir).mkdir(parents=True, exist_ok=True)

    crawl_metadata(args.api_key, args.feed_dir)
