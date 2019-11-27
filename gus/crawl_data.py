import json
import logging
from datetime import datetime

import anytree as t
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

from gus.crawlers import DataSpider, get_settings


def find_node(tree, id):
    return t.search.find_by_attr(tree, name='id', value=id)


def build_areas_tree(fpath):
    root = t.Node('root')
    nodes = {}
    with open(fpath, 'r') as f:
        for line in f:
            area = json.loads(line)
            id = area['id']
            level = area['level']
            name = area['name']
            parent_id = area.get('parentId', None)
            parent = nodes.get(parent_id, root)
            node = t.Node(name, id=id, level=level, parent=parent)
            nodes[id] = node
    return root


def render(tree):
    for pre, _, node in t.RenderTree(tree):
        print("%s%s (%s)" % (
            pre,
            node.name,
            node.id if hasattr(node, 'id') else ''))


def crawl_data(vars, areas):
    process = CrawlerProcess(settings=get_settings(), install_root_handler=True)
    process.crawl(DataSpider, vars_ids=vars, areas_ids=areas)
    process.start()


vars = [60559, 458238, 458603, 72305, 72300, 72295, 58559, 58565, 633682,
        633687, 633697, 633702, 633622, 633627, 633667, 633672, 196565, 60572,
        60573, 410600, 196562, 452355, 452356, 10514, 33484, 10515, 64428,
        64429, 151866, 151867, 289665, 289666, 804, 458615, 472362, 472363,
        1365258, 498860, 7849, 7850, 7851, 744945, 744946, 288080, 73854, 73847,
        73851, 73855, 73848, 395921, 10631, 10632, 10633, 10634, 59631, 10689,
        288096, 10691, 10693, 2090, 1508, 453827, 1241, 7614, 474443, 1230,
        148551, 410716, 410728, 377288, 73410, 58964, 58965, 64542, 64543,
        64545, 3507, 60505, 196566]



if __name__ == '__main__':
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        # FIXME For some reason files with .log extension are not shown im Intellij
        filename='log-{:%Y-%m-%d-%H-%M-%S}.txt'.format(datetime.now()),
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG
    )

    all_areas = build_areas_tree('data/areas.jl')
    subtree = t.search.find_by_attr(all_areas, value='MAZOWIECKIE')
    render(subtree)
    areas = [node.id for node in subtree.descendants] + [subtree.id]
    crawl_data(vars, areas)
