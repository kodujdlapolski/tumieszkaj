import pandas as pd

import swagger_client as gus


# TODO It would be good if Swagger defintiion from GUS contains authentication header

def get_client():
    configuration = gus.Configuration()
    configuration.debug = False
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
    unit_id = units.units_search_get(name=unit_name).results[0].id
    vars_ids = [var.id for path, name, var in variables]

    data = data_api.data_by_unit_get(var_id=vars_ids, unit_id=unit_id)

    all_series = []
    for variable, result in zip(variables, data.results):
        path, name, var = variable
        values = [value.val for value in result.values]
        index = [value.year for value in result.values]
        name = '/'.join(path + [name])
        series = pd.Series(values, index=index, name=name)
        all_series.append(series)
    df = pd.DataFrame(all_series).T
    df.index.name = 'Rok'
    return df


df = get_data('TERENY ZIELENI', 'Kielce')
data = df.to_csv('data/Kielce TERENY ZIELENI.csv', index=True)

df = get_data('TERENY ZIELENI', 'Imielin')
data = df.to_csv('data/Imielin TERENY ZIELENI.csv', index=True)

df = get_data('SPORT', 'Imielin')
data = df.to_csv('data/Imielin SPORT.csv', index=True)

df = get_data('ŚCIEŻKI ROWEROWE', 'Imielin')
data = df.to_csv('data/Imielin ŚCIEŻKI ROWEROWE.csv', index=True)
