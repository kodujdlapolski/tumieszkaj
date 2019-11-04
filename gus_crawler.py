import math

import anytree as tree
import pandas as pd
import swagger_client as gus_client
from anytree.importer import JsonImporter

class Crawler:
    MAX_PAGE_SIZE = 100

    def get_client(self):
        configuration = gus_client.Configuration()
        configuration.debug = False
        configuration.host = 'https://bdl.stat.gov.pl/api/v1'
        client = gus_client.ApiClient(configuration=configuration,
                                      header_name='X-ClientId',
                                      header_value='afeb163d-fab0-48e0-eb76-08d75c76efda')
        return client

    def __init__(self):
        client = self.get_client()
        self.subjects_api = gus_client.SubjectsApi(client)
        self.variables_api = gus_client.VariablesApi(client)
        self.data_api = gus_client.DataApi(client)
        self.units_api = gus_client.UnitsApi(client)

    def download(self, request, unit_name):
        variables = request.leaves
        vars_ids = [var.id for var in variables]
        unit = self.units_api.units_search_get(name=unit_name).results[0]
        page_size = self.MAX_PAGE_SIZE
        page = 0
        data = self.data_api.data_by_unit_get(var_id=vars_ids,
                                              unit_id=unit.id,
                                              page_size=page_size,
                                              page=page)
        pages = math.ceil(data.total_records / page_size)
        all_series = []
        while page <= pages:
            variables = sorted(variables, key=lambda v:v.id)
            results = sorted(data.results, key=lambda r:r.id)
            for variable, result in zip(variables, results):
                values = [value.val for value in result.values]
                index = [value.year for value in result.values]
                var_path = '/'.join([node.name for node in variable.path[1:]])
                series = pd.Series(values, index=index, name=var_path)
                all_series.append(series)
                page += 1
                if page <= pages:
                    data = self.data_api.data_by_unit_get(var_id=vars_ids,
                                                          unit_id=unit.id,
                                                          page_size=page_size,
                                                          page=page)

        df = pd.DataFrame(all_series).T
        df.index.name = 'Rok'
        df.sort_index(inplace=True)
        return df


    def get_download_request(self, paths):
        request = self._paths_to_tree(paths)
        online_subjects_1 = self.subjects_api.subjects_get(
            page_size=self.MAX_PAGE_SIZE).results
        for subject in request.children:
            online_subject = self._get_subject_by_name(subject.name,
                                                       online_subjects_1)
            subject.id = online_subject.id
            online_subjects_2 = [self.subjects_api.subjects_by_id_get(child_id)
                                 for child_id
                                 in online_subject.children]
            for subject in subject.children:
                online_subject = self._get_subject_by_name(subject.name,
                                                           online_subjects_2)
                subject.id = online_subject.id
                online_subjects_3 = [
                    self.subjects_api.subjects_by_id_get(child_id)
                    for child_id
                    in online_subject.children]
                for subject in subject.children:
                    online_subject = self._get_subject_by_name(subject.name,
                                                               online_subjects_3)
                    subject.id = online_subject.id
                    online_vars = self.variables_api.variables_get(
                        subject_id=subject.id,
                        page_size=self.MAX_PAGE_SIZE).results
                    for variable in subject.children:
                        online_var = self._get_var_by_name(variable.name,
                                                           online_vars)
                        variable.id = online_var.id
                        variable.level = online_var.level

        return request

    def import_request(self, fpath):
        importer = JsonImporter()
        with open(fpath, 'r') as f:
            return importer.read(f)

    def print_download_request(self, request):
        for pre, _, node in tree.RenderTree(request):
            print("%s%s (%s)" % (
                pre,
                node.name,
                node.id if hasattr(node, 'id') else ''))

    def _paths_to_tree(self, paths):
        root = tree.Node('root')
        for path in paths:
            path = path.split('/')
            current = root
            for name in path:
                child = next(
                    (node for node in current.children if node.name == name),
                    None)
                if child is None:
                    child = tree.Node(name, parent=current)
                current = child
        return root

    def _get_subject_by_name(self, name, subjects):
        matching = next(
            (subject for subject in subjects if subject.name == name), None)
        if matching is None:
            raise ValueError(f'Invalid subject name {name}')
        return matching

    def _get_var_by_name(self, name, variables):
        def get_name(v):
            parts = [v.n1, v.n2, v.n3, v.n4, v.n5]
            return ' '.join([part for part in parts if part])

        matching = next(
            (variable for variable in variables if get_name(variable) == name),
            None)
        if matching is None:
            raise ValueError(f'Invalid variable name {name}')
        return matching
