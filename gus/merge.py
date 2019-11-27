import json

import pandas as pd

from gus import tree


def absolute_name(node):
    return '/'.join([n.name for n in node.path[1:]])


def load_variables_tree(subjects_fpath, variables_fpath):
    with open(subjects_fpath, 'r') as lines:
        subjects_entries = [json.loads(line) for line in lines]
    with open(variables_fpath, 'r') as lines:
        variables_entries = [json.loads(line) for line in lines]
    variables_entries = [
        {'id': e['id'], 'parentId': e['subjectId'], 'name': e['name']}
        for e
        in variables_entries]
    return tree.build_tree(subjects_entries + variables_entries)


def load_areas_tree(fpath):
    with open(fpath, 'r') as lines:
        areas_entries = [json.loads(line) for line in lines]
    return tree.build_tree(areas_entries)


def safe_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default


def get_path_name(paths, area_id, level):
    area_path = paths.get(area_id)
    return safe_get(area_path, level, '')


def get_areas(fpath):
    areas_tree = load_areas_tree(fpath)
    areas_names = {node.id: absolute_name(node)
                   for node
                   in tree.all_nodes(areas_tree)}

    areas = pd.read_json(fpath, lines=True)
    paths = {node.id: [n.name for n in node.path[1:]]
             for node
             in tree.all_nodes(areas_tree)}
    for level in range(0, 8):
        col = f'level{level}'
        areas[col] = areas.apply(
            lambda area: get_path_name(paths, area['id'], level), axis=1)
        areas['absoluteName'] = areas.apply(
            lambda v: areas_names.get(v['id'], ''), axis=1)
    return areas


def get_variables(subjects_fpath, variables_fpath):
    variables_tree = load_variables_tree(subjects_fpath, variables_fpath)
    variables = pd.read_json(variables_fpath, lines=True)
    variables_categories = {node.id: [n.name for n in node.path[1:]]
                            for node
                            in variables_tree.leaves}
    variables_names = {node.id: absolute_name(node)
                       for node
                       in variables_tree.leaves}
    variables['absoluteName'] = variables.apply(
        lambda v: variables_names.get(v['id'], ''), axis=1)
    variables['subject'] = variables.apply(
        lambda v: variables_categories.get(v['id'])[0], axis=1)
    variables['subsubject'] = variables.apply(
        lambda v: variables_categories.get(v['id'])[1], axis=1)
    variables['subsubsubject'] = variables.apply(
        lambda v: variables_categories.get(v['id'])[2], axis=1)
    return variables

# TODO Introduce parallel reading
if __name__ == '__main__':
    data_slaskie = pd.read_json('data/data-śląskie.jl', lines=True)
    data_mazowieckie  = pd.read_json('data/data-mazowieckie.jl', lines=True)
    data = pd.concat([data_slaskie, data_mazowieckie], axis=0)
    levels = pd.read_json('data/levels.jl', lines=True)
    measures = pd.read_json('data/measures.jl', lines=True)
    areas = get_areas('data/areas.jl')
    variables = get_variables('data/subjects.jl', 'data/variables.jl')

    merged_data = data \
        .merge(
            areas.rename(
                columns={'name': 'areaName', 'level': 'areaLevel', 'id': 'areaId'}),
            left_on='areaId',
            right_on='areaId',
            suffixes=('', '_y')) \
        .merge(
            variables.rename(
                columns={'name': 'variableName', 'absoluteName': 'varAbsoluteName',
                         'id': 'variableId', 'level':'validityLevel'}),
            left_on='variableId',
            right_on='variableId',
            suffixes=('', '_y')) \
        .merge(
            measures.rename(columns={'name': 'measureName', 'id': 'measureId'}),
            left_on='measureId',
            right_on='measureId',
            suffixes=('', '_y'))

    columns = ['level0', 'level1', 'level2', 'level3', 'level4', 'level5',
               'level6', 'level7', 'areaId', 'areaName', 'areaLevel',
               'subject', 'subsubject', 'subsubsubject', 'variableId',
               'variableName', 'validityLevel',
               'year',
               'value', 'measureName']

    merged_data = merged_data[columns].sort_values(by=columns)
    merged_data.to_csv('data/merged_data.csv.gz', compression='gzip')
    merged_data.to_hdf('data/merged_data.h5', key='gus_bdl')
