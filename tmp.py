
import anytree as tree
import swagger_client as gus


# TODO It would be good if Swagger defintiion from GUS contains authentication header

def get_client():
    configuration = gus.Configuration()
    configuration.debug = True
    configuration.host = 'https://bdl.stat.gov.pl/api/v1'
    client = gus.ApiClient(configuration=configuration,
                           header_name='X-ClientId',
                           header_value='afeb163d-fab0-48e0-eb76-08d75c76efda')
    return client


client = get_client()
subjects_api = gus.SubjectsApi(client)
variables_api = gus.VariablesApi(client)
data_api = gus.DataApi(client)
units = gus.UnitsApi(client)


def get_subject(subject_name):
    results = subjects_api.subjects_search_get(name=subject_name,
                                               page_size=100).results
    subject = next((result
                    for result
                    in results
                    if result.name == subject_name),
                   None)
    return subject


def get_subjects_with_vars(subject_id, path=None):
    # TODO Get also path from here to root through parent ids

    leaves = []
    subject = subjects_api.subjects_by_id_get(subject_id)
    path = [subject.name] if path is None else path + [subject.name]
    if subject.has_variables:
        leaves.append((path, subject))
    else:
        for child_id in subject.children:
            leaves.extend(get_subjects_with_vars(child_id, path))
    return leaves


def get_variable_name(variable):
    l = [variable.n1, variable.n2, variable.n3, variable.n4,
         variable.n4, variable.n5]
    return " ".join([s for s in l if s])


def get_variables(subject_name):
    subject = get_subject(subject_name)
    subjects = get_subjects_with_vars(subject.id)
    variables = []
    for path, subject in subjects:
        results = variables_api.variables_get(subject_id=subject.id).results
        variables.extend(
            [(path, get_variable_name(result), result) for result in results])
    return variables


def get_data(subject_name, unit_name):
    variables = get_variables(subject_name)





def step_1():

    subjects_names = ['TERENY ZIELENI', 'BUDOWNICTWO MIESZKANIOWE', 'SPORT',
                      'ŚCIEŻKI ROWEROWE', 'BUDOWNICTWO MIESZKANIOWE (grupa w przebudowie)',
                      'BUDOWNICTWO NIEMIESZKANIOWE (DANE KWARTALNE)']
    units_names = ['Imielin', 'Kielce']

    for unit_name in units_names:
        for subject_name in subjects_names:
            df = get_data(subject_name, unit_name)
            df.to_csv(f'data/{unit_name}/{subject_name}.csv', index=True)


def step_2():
    subjects_names = ['RYNKOWA SPRZEDAŻ LOKALI MIESZKALNYCH', 'ZASOBY MIESZKANIOWE']
    units_names = ['Powiat bieruńsko-lędziński']
    for unit_name in units_names:
        for subject_name in subjects_names:
            df = get_data(subject_name, unit_name)
            df.to_csv(f'data/{unit_name}/{subject_name}.csv', index=True)

# This is highly ineffective and results in rejections
def build_online_gus_tree():
    online_gus = tree.Node('online_gus')
    parent = online_gus
    for online_subject in subjects_api.subjects_get().results:
        parent = tree.Node(online_subject.name, id=online_subject.id, parent=parent)
        for subject_id in online_subject.children:
            online_subject = subjects_api.subjects_by_id_get(subject_id)
            parent = tree.Node(online_subject.name, id=subject_id, parent=parent)
            for subject_id in online_subject.children:
                for online_var in variables_api.variables_get(subject_id=subject_id).results:
                    parts = [online_var.n1, online_var.n2, online_var.n3,
                             online_var.n4, online_var.n5]
                    name = ' '.join([part for part in parts if part])
                    tree.Node(name, id=online_var.id, parent=parent)

    print(tree.RenderTree(online_gus))






#step_2()

#print(subjects_api.subjects_by_id_get('P3787'))

# TODO We want to download variables on a certain basis, how often things change?




gus = paths_to_tree(paths)
gus.id = 0

print(tree.RenderTree(gus))










