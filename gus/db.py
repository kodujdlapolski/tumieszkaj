import json
import os

import anytree
from tqdm import tqdm

from gus.tree import (
    render,
    build_tree
)


class MetadataDB:

    def __init__(self, metadata_dir):
        self.metadata_dir = metadata_dir
        areas_fpath = os.path.join(metadata_dir, 'areas.jl')
        self.all_areas = self.build_areas_tree(areas_fpath)
        subjects_fpath = os.path.join(metadata_dir, 'subjects.jl')
        vars_fpath = os.path.join(metadata_dir, 'variables.jl')
        self.all_vars = self.build_variables_tree(subjects_fpath, vars_fpath)

    def find_subareas_ids(self, root_area_name, level=None, kinds=None):
        return set([area.id
                    for area
                    in self.find_subareas(root_area_name, level, kinds)])

    def find_subareas_names(self, root_area_name, level=None, kinds=None):
        return set([area.name
                    for area
                    in self.find_subareas(root_area_name, level, kinds)])

    def find_variables_ids(self, subject_id):
        return [var.id for var in self.find_variables(subject_id)]

    def find_variables(self, subject_id):
        root = anytree.search.find_by_attr(self.all_vars,
                                                  name='id',
                                                  value=subject_id)
        return [var for var in root.leaves]

    def find_subareas(self, root_area_name, level=None, kinds=None):
        subtrees = anytree.search.findall_by_attr(self.all_areas,
                                                  value=root_area_name)
        areas = set()
        for subtree in subtrees:
            render(subtree)
            areas.update(subtree.descendants)
            areas.add(subtree)

        if not level is None:
            areas = set(area for area in areas if area.level == level)
        if not kinds is None:
            areas = set(area for area
                        in areas
                        if area.level != 6 or area.kind in kinds)

        return areas

    def build_variables_tree(self, subjects_fpath, vars_fpath):
        with open(subjects_fpath, 'r') as lines:
            subjects_entries = [json.loads(line)
                                for line
                                in tqdm(lines, desc='Loading GUS BDL subjects')]
        with open(vars_fpath, 'r') as lines:
            variables_entries = [json.loads(line)
                                 for line
                                 in tqdm(lines, desc='Loading GUS BDL variables')]
            variables_entries = [{'id': e['id'],
                                  'parentId': e['subjectId'],
                                  'name': e['name']}
                                 for e
                                 in variables_entries]
        root = build_tree(subjects_entries + variables_entries)
        return root

    def build_areas_tree(self, fpath):
        root = anytree.Node('root')
        nodes = {}
        with open(fpath, 'r') as f:
            for line in tqdm(f, desc='Loading GUS BDL areas...'):
                area = json.loads(line)
                id = area['id']
                level = area['level']
                name = area['name']
                parent_id = area.get('parentId', None)
                try:
                    kind = int(area.get('kind', None))
                except TypeError:
                    kind = None
                parent = nodes.get(parent_id, root)
                node = anytree.Node(name, id=id, level=level, kind=kind,
                                    parent=parent)
                nodes[id] = node
        return root
