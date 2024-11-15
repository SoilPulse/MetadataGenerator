# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""

from soilpulse-core.project_management import ProjectManager
from soilpulse-core.data_publishers import *
from soilpulse-core.resource_managers.filesystem import *
from soilpulse-core.resource_managers.mysql import *
from soilpulse-core.resource_managers.xml import *
from soilpulse-core.resource_managers.data_structures import *
from soilpulse-core.resource_managers.json import *
from soilpulse-core.db_access import DBconnector, MySQLConnector, NullConnector

import pytest
from pathlib import Path
import os
from shutil import rmtree

# example DOI record
example = {"name": "NFDItest", "doi": "10.5281/zenodo.8345022"}
files = [Path("testfiles","testdata.csv").absolute().as_posix(), Path("testfiles","testtexture.csv").absolute().as_posix()]

example_outputs = {"RA": "DataCite", # which RA should be returned from doi.org
                   "containers_files_loaded": 6, # number of top level containers soilpulse should identify
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
                     }

# test DOI metadata retrieval and registration agency name extraction
def test_RA_valid():
    assert ProjectManager.getRegistrationAgencyOfDOI(example['doi']) == example_outputs['RA']

def test_RA_invalid():
    with pytest.raises(Exception):
        ProjectManager.getRegistrationAgencyOfDOI("doi")


##### test ProjectManager creation, published files download, initial mapping to containers and project deletion
##### with MySQL storage

## Initiate Project
# user_id will be later managed by some login framework in streamlit - user can access only own resources
project = ProjectManager(MySQLConnector(), user_id=1, **example)
project.keepFiles = False
## Download Files
project.downloadPublishedFiles()
# save the project to storage
project.updateDBrecord()

project_dir = os.path.join(project.dbconnection.project_files_root, project.dbconnection.dirname_prefix + str(project.id))

def test_project_established_mysql():
    # get the cursor from database connection of the project
    thecursor = project.dbconnection.db_connection.cursor(dictionary=True)
    query = f"SELECT `name`, `doi`, `keep_files` FROM {project.dbconnection.projectsTableName} WHERE `id` = 1"
    thecursor.execute(query)
    results = thecursor.fetchone()
    thecursor.close()
    # check the project attributes saved in database
    assert results['name'] == example['name']
    assert results['doi'] == example['doi']
    assert results['keep_files'] == 0
    # check the project directory and dataset subdirectory were created
    assert os.path.isdir(project_dir)
    assert os.path.isdir(os.path.join(project_dir, project.dbconnection.datasets_directory_name))
    # check that the DOI and publisher metadata were downloaded and stored
    assert os.path.isfile(os.path.join(project_dir, "DOI_metadata.json"))
    assert os.path.isfile(os.path.join(project_dir, "Publisher_metadata.json"))
    # check if the containers were correctly created
    assert len(project.containerTree) == 6

def test_project_saved_mysql():
    # get the cursor from database connection of the project
    thecursor = project.dbconnection.db_connection.cursor(dictionary=True)
    query = f"SELECT `id_local`, `name`, `type`, `relative_path` FROM {project.dbconnection.containersTableName} " \
            f"WHERE `project_id` = 1 " \
            f"ORDER BY `id_local` ASC "
    thecursor.execute(query)
    results = thecursor.fetchall()
    thecursor.close()
    # check the containers count and some attributes
    assert len(results) == 15
    assert results[0]['name'] == "DOI metadata"
    assert results[1]['name'] == "Publisher metadata"
    assert results[0]['type'] == "json"
    assert results[1]['type'] == "json"
    assert results[0]['relative_path'] == "DOI_metadata.json"
    assert results[1]['relative_path'] == "Publisher_metadata.json"

project.keepFiles = True

def test_upload_files_mysql():
    project.uploadFilesFromSession(files)
    project.updateDBrecord()
    # check the files exist in project directory
    assert os.path.basename(files[0]) in os.listdir(project_dir)
    assert os.path.basename(files[1]) in os.listdir(project_dir)

    # check the containers were created
    thecursor = project.dbconnection.db_connection.cursor()
    filenames = ["'"+os.path.basename(f)+"'" for f in files]
    query = f"SELECT COUNT(*) FROM {project.dbconnection.containersTableName} " \
            f"WHERE `relative_path` IN ({', '.join(filenames)}) AND `project_id` = {project.id}"
    thecursor.execute(query)
    cont_count = thecursor.fetchone()[0]
    thecursor.close()
    assert cont_count == 2

def test_project_deleted_mysql():
    # check deleting published files
    project.deleteDownloadedFiles()
    assert not "NFDI4Earth_D1.3.12.pdf" in os.listdir(project_dir)
    assert os.path.basename(files[0]) in os.listdir(project_dir)
    # check deleting upladed files
    project.deleteUploadedFiles()
    assert not os.path.basename(files[0]) in os.listdir(project_dir)
    assert not os.path.join(project_dir, "DOI_metadata.json") in os.listdir(project_dir)

    # check deleting the whole project
    project.dbconnection.deleteProject(project)
    assert not os.path.isdir(project_dir)
    # check if the database entry was removed
    thecursor = project.dbconnection.db_connection.cursor()
    query = f"SELECT COUNT(*) FROM {project.dbconnection.projectsTableName} WHERE `id` = {project.id}"
    thecursor.execute(query)
    count = thecursor.fetchone()[0]
    thecursor.close()
    assert count == 0

# def test_delete_project():
#     project.deleteDownloadedFiles()
#     project.deleteUploadedFiles()
#     project.deleteAllProjectFiles()
#     rmtree(project.temp_dir)
#     assert not Path(project.temp_dir).is_dir()

##### test ProjectManager creation, published files download, initial mapping to containers and project deletion
##### with filesystem storage

## Initiate Project
# user_id will be later managed by some login framework in streamlit - user can access only own resources
project2 = ProjectManager(NullConnector(), user_id=1, **example)
project2.keepFiles = False
## Download Files
project2.downloadPublishedFiles()
# save the project to storage
project2.updateDBrecord()

project2_dir = os.path.join(project2.dbconnection.project_files_root, project2.dbconnection.dirname_prefix + str(project2.id))

def test_project_established_null():
    # check the project attributes saved in file
    project_json = os.path.join(project2_dir, project2.dbconnection.project_attr_filename)
    with open(project_json, "r") as f:
        attributes = json.load(f)
    assert attributes["name"] == example['name']
    assert attributes["doi"] == example['doi']
    assert attributes["keep_files"] == 0

    # check the project directory and dataset subdirectory were created
    assert os.path.isdir(project2_dir)
    assert os.path.isdir(os.path.join(project2_dir, project2.dbconnection.datasets_directory_name))
    # check that the DOI and publisher metadata were downloaded and stored
    assert os.path.isfile(os.path.join(project2_dir, "DOI_metadata.json"))
    assert os.path.isfile(os.path.join(project2_dir, "Publisher_metadata.json"))
    # check if the containers were correctly created
    assert len(project2.containerTree) == 6

def test_project_saved_null():
    # load the containers dump from file
    containers_json = os.path.join(project2_dir, project2.dbconnection.containers_attr_filename)
    with open(containers_json, "r") as f:
        containers = json.load(f)

    # check the containers count and some attributes
    assert len(containers) == 6
    assert containers["1"]["name"] == "DOI metadata"
    assert containers["2"]["name"] == "Publisher metadata"
    assert containers["1"]["type"] == "json"
    assert containers["2"]["type"] == "json"
    assert containers["1"]["relative_path"] == "DOI_metadata.json"
    assert containers["2"]["relative_path"] == "Publisher_metadata.json"

project2.keepFiles = True

def test_upload_files_null():
    project2.uploadFilesFromSession(files)
    project2.updateDBrecord()
    # check the files exist in project directory
    assert os.path.basename(files[0]) in os.listdir(project2_dir)
    assert os.path.basename(files[1]) in os.listdir(project2_dir)

    # check the containers were created
    # load the containers dump from file
    containers_json = os.path.join(project2.dbconnection.project_files_root, project2.dbconnection.dirname_prefix + str(project2.id),
                                project2.dbconnection.containers_attr_filename)
    with open(containers_json, "r") as f:
        containers = json.load(f)

    # check the containers count got bigger
    assert len(containers) == 8

def test_project_deleted_null():
    # check deleting published files
    project2.deleteDownloadedFiles()
    assert not "NFDI4Earth_D1.3.12.pdf" in os.listdir(project2_dir)
    assert os.path.basename(files[0]) in os.listdir(project2_dir)
    # check deleting upladed files
    project2.deleteUploadedFiles()
    assert not os.path.basename(files[0]) in os.listdir(project2_dir)
    assert not os.path.join(project2_dir, "DOI_metadata.json") in os.listdir(project2_dir)

    # check deleting the whole project
    project2.dbconnection.deleteProject(project2)
    assert not os.path.isdir(project2_dir)

#
# project.getContainerByID(10).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})
#
# ##### save project
# project.updateDBrecord()
#
# project.getContainerByID(10).removeAllConcepts()
#
# project.getContainerByID(6).removeAllConcepts()
# # assigning a concept to container
# project.getContainerByID(9).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})
# # this one is wrong and shoouldn't be there ...
# project.getContainerByID(8).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})
# project.getContainerByID(8).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_4260"})
# project.getContainerByID(9).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_4260"})
# # removing a concept from container
# # ... so it's removed
# project.getContainerByID(9).removeConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})
#
#
# ##### save project
# project.updateDBrecord()
#
# @pytest.mark.parametrize("example", [example])
# def test_project_doi_retrieved(example):
#     assert project.DOImetadata['data']['id'] == example["doi"]
#
#
# def test_project_files():
#     if 'server' in dir(project.dbconnection):
#         assert True
#     else:
#         assert "_project.json" in os.listdir(project.temp_dir)
#
#
#
# @pytest.mark.parametrize("example", [example])
# def test_project_container_tree_with_files(example):
#     assert len(project.containerTree)==example['asserts']['containers_files_loaded']
#
#
# @pytest.mark.parametrize("example", [example])
# def test_project_files_loaded(example):
#     assert example['asserts']['file_in_dir'] in os.listdir(project.temp_dir)
#
#
# def test_project_files_container():
#     if 'server' in dir(project.dbconnection):
#         assert True
#     else:
#         assert "_containers.json" in os.listdir(project.temp_dir)
#
#
# ##### load project
# project_load = ProjectManager(dbcon, user_id, **{"id": project.id})
#
# @pytest.mark.parametrize("example", [(example)])
# def test_project_loaded(example):
#     assert project_load.doi == example["doi"]
#
#
# @pytest.mark.parametrize("example", [example_5])
# def test_project_loaded_container_tree(example):
#     assert len(project_load.containerTree)==example['asserts']['containers_files_loaded']
#
#
# @pytest.mark.parametrize("example", [example_5])
# def test_table_container(example):
#     table = project.getContainerByID(example['asserts']['table_container_ID']).containers[0]
#     if table.containerType == 'table':
#         for x in table.containers:
#             if not x.containerType == 'column':
#                 result = False
#         result = True
#     assert result
#
# @pytest.mark.parametrize("example", [example_5])
# def test_concept_assignment(example):
#     result = 0
#     for x in example['asserts']['concepts']:
#         if not project.getContainerByID(int(x)).concepts == example['asserts']['concepts'][x]:
#             result += 1
#     assert result == 0
#

