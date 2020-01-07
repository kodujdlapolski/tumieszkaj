import json
import os

import anytree

from gus.tree import render


class MetadataDB:

    def __init__(self, metadata_dir):
        self.metadata_dir = metadata_dir
        areas_fpath = os.path.join(metadata_dir, 'areas.jl')
        self.all_areas = self.build_areas_tree(areas_fpath)

    def find_areas(self, area_name):
        subtrees = anytree.search.findall_by_attr(self.all_areas,
                                                  value=area_name)
        areas = set()
        for subtree in subtrees:
            render(subtree)
            areas.update([node.id for node in subtree.descendants])
            areas.add(subtree.id)
        return areas

    def build_areas_tree(self, fpath):
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