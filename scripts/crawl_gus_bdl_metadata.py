import argparse
import logging
from datetime import datetime
from pathlib import Path

from scrapy.utils.log import configure_logging

from gus.crawlers import crawl_metadata

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
