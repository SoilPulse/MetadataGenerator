# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 13:59:52 2024

@author: JL
"""

from frictionless import Package, Pipeline, steps
import os
import json
from pathlib import Path
import simpleeval

#project = {}

#project['sourcedir'] = "catalogue/temp_1/"


def load_sp_datapackage(project):
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
            pipe = Pipeline(steps=simpleeval.simple_eval(f.read()))

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



TUBAF = load_sp_datapackage({"sourcedir": "catalogue/temp_1/"})
RIES = load_sp_datapackage({"sourcedir": "catalogue/temp_2/"})
