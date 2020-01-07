import json
import os

import anytree
from scrapy.crawler import CrawlerProcess

from gus.crawlers import (
    DataSpider,
    get_settings
)
from gus.tree import render


def build_areas_tree(fpath):
    root = anytree.Node('root')
    nodes = {}
    with open(fpath, 'r') as f:
        for line in f:
            area = json.loads(line)
            id = area['id']
            level = area['level']
            name = area['name']
            parent_id = area.get('parentId', None)
            parent = nodes.get(parent_id, root)
            node = anytree.Node(name, id=id, level=level, parent=parent)
            nodes[id] = node
    return root


def crawl_data(vars, areas, api_key=None, feed_dir=None):
    if feed_dir is None:
        raise ValueError('feed_dir is required')

    process = CrawlerProcess(settings=get_settings(api_key),
                             install_root_handler=True)
    process.crawl(DataSpider, vars_ids=vars, areas_ids=areas, feed_dir=feed_dir)
    process.start()


def find_areas(metadata_dir, area_name):
    areas_fpath = os.path.join(metadata_dir, 'areas.jl')
    all_areas = build_areas_tree(areas_fpath)
    subtrees = anytree.search.findall_by_attr(all_areas, value=area_name)
    areas = set()
    for subtree in subtrees:
        render(subtree)
        areas.update([node.id for node in subtree.descendants])
        areas.add(subtree.id)
    return areas
