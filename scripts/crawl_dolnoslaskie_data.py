import argparse
import logging
from datetime import datetime
from pathlib import Path

from scrapy.utils.log import configure_logging

from gus.crawlers import crawl_data
from gus.db import MetadataDB

if __name__ == '__main__':
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        # FIXME For some reason files with .log extension are not shown im Intellij
        filename='log-{:%Y-%m-%d-%H-%M-%S}.txt'.format(datetime.now()),
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG
    )

    if __name__ == '__main__':
        configure_logging(install_root_handler=False)
    logging.basicConfig(
        # FIXME For some reason files with .log extension are not shown im Intellij
        filename='log-{:%Y-%m-%d-%H-%M-%S}.txt'.format(datetime.now()),
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG
    )

    parser = argparse.ArgumentParser(description='Crawls data from GUS BDL')
    parser.add_argument('-k', '--api-key',
                        help='GUS BDL API key',
                        type=str,
                        required=True)
    parser.add_argument('-f', '--feed-dir',
                        help='Directory to store crawlers output',
                        type=str,
                        required=True)
    parser.add_argument('-m', '--metadata-dir',
                        help='Directory to read metadata crawled from GUS BDL',
                        type=str,
                        required=True)

    args = parser.parse_args()

    Path(args.feed_dir).mkdir(parents=True, exist_ok=True)

    vars = [60559, 458238, 458603, 72305, 72300, 72295, 58559, 58565, 633682,
            633687, 633697, 633702, 633622, 633627, 633667, 633672, 196565,
            60572, 60573, 410600, 196562, 452355, 452356, 10514, 33484, 10515,
            64428, 64429, 151866, 151867, 289665, 289666, 804, 458615, 472362,
            472363, 1365258, 498860, 7849, 7850, 7851, 744945, 744946, 288080,
            73854, 73847, 73851, 73855, 73848, 395921, 10631, 10632, 10633,
            10634, 59631, 10689, 288096, 10691, 10693, 2090, 1508, 453827, 1241,
            7614, 474443, 1230, 148551, 410716, 410728, 377288, 73410, 58964,
            58965, 64542, 64543, 64545, 3507, 60505, 196566]

    metadata = MetadataDB(args.metadata_dir)
    areas = metadata.find_subareas_ids('DOLNOŚLĄSKIE')

    crawl_data(vars, areas, args.api_key, args.feed_dir)
