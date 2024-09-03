# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""

from soilpulse.project_management import ProjectManager, DatabaseEntryError
import soilpulse.resource_managers.filesystem
import soilpulse.resource_managers.mysql
import soilpulse.resource_managers.xml
import soilpulse.resource_managers.json
from soilpulse.data_publishers import PublisherFactory, DOIdataRetrievalException
#import soilpulse.metadata_scheme
from soilpulse.db_access import EntityKeywordsDB, DBconnector

import pytest
from pathlib import Path
import os
from shutil import rmtree

project_files_dir_name = "project_files"
project_files_root = Path(os.path.join(Path.home(), "soilpulse_test", project_files_dir_name))
print(project_files_root)
project_files_root.mkdir(parents=True, exist_ok=True)


# example DOI records that can be used
#example_1 = {"name": "Jonas Lenz's dissertation package", "doi": "10.5281/zenodo.6654150"}
#example_2 = {"name": "", "doi": "10.5281/zenodo.6654150"}
#example_3 = {"name": "Michael Schmuker's neuromorphic_classifiers", "doi": "10.5281/zenodo.18726"}  # more lightweight repo
#example_4 = {"name": "Ries et al.", "doi": "10.6094/unifr/151460"}
example_5 = {"name": "NFDItest",
             "doi": "10.5281/zenodo.8345022",
             "asserts": {
                     "RA": "DataCite", # which RA should be returned from doi.org
                     "containers_files_loaded": 6, # # number of top level containers soilpulse should identify
                     "file_in_dir": "NFDI4Earth_D1.3.12.pdf", # a file of the resource, indicating file download was succesfull
                     "table_container_ID": 6, # The ID of a table container of the Resource
                     "concepts":
                         {
                             "8":[
                                 {'vocabulary': 'AGROVOC',
                                  'uri': 'http://aims.fao.org/aos/agrovoc/c_64a2abf9'},
                                 {'vocabulary': 'AGROVOC',
                                  'uri': 'http://aims.fao.org/aos/agrovoc/c_4260'}
                                 ],
                             "9": [{'vocabulary': 'AGROVOC', 'uri': 'http://aims.fao.org/aos/agrovoc/c_4260'}],
                             "10":[],
                         }
                     },
             }

# test DOI retrieval
@pytest.mark.parametrize("example", [example_5])
def test_RA_valid(example):
    assert ProjectManager.getRegistrationAgencyOfDOI(example['doi']) == example['asserts']['RA']

def test_RA_invalid():
    with pytest.raises(Exception):
        ProjectManager.getRegistrationAgencyOfDOI("doi")


# test Project Management

# user identifier that will be later managed by some login framework in streamlit
# it's needed for loading ProjectManagers from database - user can access only own resources
user_id = 1
dbcon = DBconnector.get_connector(project_files_root=project_files_root)


##### TODO: How to parametrize the project to be used in global scope?
##### Initiate Project
project = ProjectManager(dbcon, user_id, **example_5)
project.keepFiles = False


##### Download Files
project.downloadPublishedFiles()

project.getContainerByID(10).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})

##### save project
project.updateDBrecord()

project.getContainerByID(10).removeAllConcepts()

project.getContainerByID(6).removeAllConcepts()
# assigning a concept to container
project.getContainerByID(9).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})
# this one is wrong and shoouldn't be there ...
project.getContainerByID(8).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})
project.getContainerByID(8).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_4260"})
project.getContainerByID(9).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_4260"})
# removing a concept from container
# ... so it's removed
project.getContainerByID(9).removeConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})


##### save project
project.updateDBrecord()

@pytest.mark.parametrize("example", [example_5])
def test_project_doi_retrieved(example):
    assert project.DOImetadata['data']['id'] == example["doi"]


def test_project_files():
    if 'server' in dir(project.dbconnection):
        assert True
    else:
        assert "_project.json" in os.listdir(project.temp_dir)



@pytest.mark.parametrize("example", [example_5])
def test_project_container_tree_with_files(example):
    assert len(project.containerTree)==example['asserts']['containers_files_loaded']


@pytest.mark.parametrize("example", [example_5])
def test_project_files_loaded(example):
    assert example['asserts']['file_in_dir'] in os.listdir(project.temp_dir)


def test_project_files_container():
    if 'server' in dir(project.dbconnection):
        assert True
    else:
        assert "_containers.json" in os.listdir(project.temp_dir)


##### load project
project_load = ProjectManager(dbcon, user_id, **{"id": project.id})

@pytest.mark.parametrize("example", [(example_5)])
def test_project_loaded(example):
    assert project_load.doi == example["doi"]


@pytest.mark.parametrize("example", [example_5])
def test_project_loaded_container_tree(example):
    assert len(project_load.containerTree)==example['asserts']['containers_files_loaded']


@pytest.mark.parametrize("example", [example_5])
def test_table_container(example):
    table = project.getContainerByID(example['asserts']['table_container_ID']).containers[0]
    if table.containerType == 'table':
        for x in table.containers:
            if not x.containerType == 'column':
                result = False
        result = True
    assert result

@pytest.mark.parametrize("example", [example_5])
def test_concept_assignment(example):
    result = 0
    for x in example['asserts']['concepts']:
        if not project.getContainerByID(int(x)).concepts == example['asserts']['concepts'][x]:
            result += 1
    assert result == 0

def test_clear_test_project():
    project.deleteDownloadedFiles()
    project.deleteUploadedFiles()
    project.deleteAllProjectFiles()
    rmtree(project.temp_dir)
    assert not Path(project.temp_dir).is_dir()
