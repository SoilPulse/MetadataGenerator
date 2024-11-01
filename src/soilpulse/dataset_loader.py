# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 13:59:52 2024

@author: JL
"""

from frictionless import Package, Pipeline, steps, transform
import os
import json
from pathlib import Path

#project = {}

#project['sourcedir'] = "catalogue/temp_1/"


def load_sp_datapackage(project):
#    project = {"sourcedir": "catalogue/temp_1/"}
    project['prim_path'] = os.path.normpath(project['sourcedir']+"primary_package.json")
    project['meta_path'] = os.path.normpath(project['sourcedir']+"to_publish/Publisher_metadata.json")
    project['pipe_path'] = os.path.normpath(project['sourcedir']+"to_publish/pipe.txt")
    project['targ_path'] = os.path.normpath(project['sourcedir']+"to_publish/piped_package.json")

    with open(project['meta_path'], 'r') as f:
        meta = json.load(f)

    # get target descriptor
    project[meta['doi']+'targ'] = Package(project['targ_path'])

    # try to load and validate target resource, else load primary descriptor and redo pipeline steps
    valid = project[meta['doi']+'targ'].validate()
    if valid.valid:
        return project[meta['doi']+'targ']
    else:
        with open(project['pipe_path'], 'r') as f:
            pipe = Pipeline(steps=eval(f.read()))

        project[meta['doi']] = Package(project['prim_path'])
        project[meta['doi']].transform(pipe)
        tables_path = Path(os.path.join(project['sourcedir'], "to_publish/tables"))
        tables_path.mkdir(parents=True, exist_ok=True)

        for table in project[meta['doi']].resources:
            table_path = os.path.normpath(
                os.path.join(
                    tables_path,
                    table.name+
                    ".csv"))
            if not os.path.isfile(table_path):
                # for some reason table meta of TUBAF example can only be written in second try, so this is a quickfix...
                try:
                    table.convert(to_path=table_path)
#                    print("written in first attempt")
                except:
                    table.convert(to_path=table_path)
#                    print("written in second attempt")

        valid = project[meta['doi']+'targ'].validate()
        if valid.valid:
            return project[meta['doi']+'targ']
        else:
            raise ("Failed to load project.")


def _get_agrovoc_dump():
    import pickle

    with open("agrov.dump", 'rb') as handle:
        ret = pickle.load(handle)
    optio = {r["concept"]["value"]:
             r["label"]["value"] for r in ret["results"]["bindings"]}
    return optio

optio = _get_agrovoc_dump()

def get_dataset_concepts(dataset, vocab = None):
    concepts = []
    for z in dataset.resources:
        for x in z.schema.fields:
            y = x.to_descriptor()
            if 'concept' in y:
                if isinstance(y['concept'], list):
                    concepts += [y['concept']]
                else:
                    concepts += [[y['concept']]]
    if vocab:
        labels = []
        for z in concepts:
            z_label = []
            for y in z:
                if 'agrovoc' in y:
                    z_label += [vocab[y]]
                else:
                    z_label += [y]
            labels += [z_label]
        concepts = labels
    return(concepts)


def view_sp_resource(resource, fields = None, row_filters = []):
    view = resource.to_copy()
    view = transform(
        view,
        steps =
        [
            steps.table_normalize()
        ]
        )
    if fields:
        for y in view.schema.to_descriptor()['primaryKey']:
            if not y in fields:
                fields = fields + [y]
        view = transform(
            view,
            steps=[
                steps.field_filter(names=fields),
            ]
            )
    for x in row_filters:
        view = transform(
            view,
            steps=[
                steps.row_filter(formula=x)
            ]
            )
    return view


def get_sp_data(dataset, fielddefinition):
    view = dataset.to_copy()
    for z in dataset.resources:
        resourcefields = []
        row_filters = []
        for fieldit in fielddefinition:
            for resfield in z.schema.fields:
                get = True
                resfield = resfield.to_descriptor()
                if 'name' in fieldit:
                    if not fieldit['name'] == resfield['name']:
                        get = False
                if 'concept' in fieldit:
                    if not 'concept' in resfield:
                        get = False
                    elif not fieldit['concept'] == resfield['concept']:
                        get = False
                if 'unit' in fieldit:
                    if not 'unit' in resfield:
                        get = False
                    elif not fieldit['unit'] == resfield['unit']:
                        get = False
                if get:
                    resourcefields += [resfield['name']]
                    if 'row_filters' in fieldit:
                        row_filters += fieldit['row_filters']
        if len(resourcefields)>0:
            view.remove_resource(z.name)
            z = view_sp_resource(z, resourcefields, row_filters = row_filters)
            view.add_resource(z)
        else:
            view.remove_resource(z.name)
    return view


def merge_foreign_keys(dataset):
    view = dataset.to_copy()
    if len(view.resources)>1:
        for y in view.resources:
            if y.schema.foreign_keys and len(y.schema.foreign_keys)>0:
                for x in y.schema.foreign_keys:
                    if x['fields'] == x['reference']['fields']:
                        try:
                            transform(
                                source = y,
                                steps = [
                                    steps.table_normalize(),
                                    steps.table_join(
                                        resource=x['reference']['resource'],
                                        field_name=x['fields'],
#                                        mode = 'outer'
                                        )
                                    ]
                            )
                            y.foreign_keys=[]
                        except:
                            y = transform(
                                source = y,
                                steps = [
                                    steps.table_normalize(),
                                    steps.table_join(
                                        resource=x['reference']['resource'],
                                        field_name=x['fields'],
#                                        mode = 'outer'
                                        )
                                    ]
                            )
                            y.foreign_keys=[]
    return view


TUBAF = load_sp_datapackage({"sourcedir": "catalogue/temp_1/"})
multitable = load_sp_datapackage({"sourcedir": "catalogue/temp_2/"})

Ries = load_sp_datapackage({"sourcedir": "catalogue/temp_4/"})
view_sp_resource(TUBAF.resources[0], fields = ['SigP'], row_filters = ['SigP >9', 'SigP < 12']).to_pandas()
get_dataset_concepts(TUBAF)

get_sp_data(TUBAF, fielddefinition=[{'name': 'SigP'}])

view = get_sp_data(
    TUBAF,
    fielddefinition=[
        {'name': 'SigP',
         'row_filters': ['SigP > 10']
         },
        {'unit': 'g/l',
         'row_filters': ['not sedconc == None and sedconc >=300']
         }
        ]
    )


view = merge_foreign_keys(
    get_sp_data(
        TUBAF,
        fielddefinition=[
            {'name': 'SigP',
             'row_filters': ['No == "8"']
             },
            {'unit': 'g/l',
             'row_filters': ['not sedconc == None', 'No == "8"']
             }
            ]
        )
    )

try:
    view.extract()
except:
    view.extract()

# model requirements can be defined by row constraints
#from frictionless import validate, checks, transform
#validate(TUBAF.resources[0],
#         checks=[
#             checks.row_constraint(formula="fSi + mSi + cSi == SILT"),
#             checks.row_constraint(formula="fSa + mSa + cSa == SAND"),
#             checks.row_constraint(formula="SILT + SAND + CLAY == 100")
#             ]
#         )
