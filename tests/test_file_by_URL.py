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
example_5 = {"name": "csvtest",
             "url_list": [ProjectManager.SourceFile(id = 1,
                                                    filename = "testdata.csv",
                                                    source_url = "https://github.com/SoilPulse/MetadataGenerator/blob/main/tests/testfiles/testdata.csv"),
                          ProjectManager.SourceFile(id = 1,
                                                    filename = "testliteral.csv",
                                                    source_url = "https://github.com/SoilPulse/MetadataGenerator/blob/main/tests/testfiles/testliteral.csv"),
                          ProjectManager.SourceFile(id = 1,
                                                    filename = "testtexture.csv",
                                                    source_url = "https://github.com/SoilPulse/MetadataGenerator/blob/main/tests/testfiles/testtexture.csv"),
                         ],
             "asserts": {
                     "RA": None, # which RA should be returned from doi.org
                     "containers_files_loaded": 3, # # number of top level containers soilpulse should identify
                     "file_in_dir": "testdata.csv", # a file of the resource, indicating file download was succesfull
                     "table_container_ID": 1, # The ID of a table container of the Resource
                     },
             }


# test Project Management - file upload

# user identifier that will be later managed by some login framework in streamlit
# it's needed for loading ProjectManagers from database - user can access only own resources
user_id = 1
dbcon = DBconnector.get_connector(project_files_root=project_files_root)

projects_before = dbcon.getProjectsOfUser(1)

##### TODO: How to parametrize the project to be used in global scope?
##### Initiate Project
project = ProjectManager(dbcon, user_id, **example_5)
project.keepFiles = False


##### Download Test File
project.downloadPublishedFiles(list = example_5['url_list'])

@pytest.mark.parametrize("example", [example_5])
def test_project_container_tree_with_files(example):
    assert len(project.containerTree)==example['asserts']['containers_files_loaded']


@pytest.mark.parametrize("example", [example_5])
def test_project_files_loaded(example):
    assert example['asserts']['file_in_dir'] in os.listdir(project.temp_dir)


##### save project
project.updateDBrecord()

projects_invoked = dbcon.getProjectsOfUser(1)

def test_project_files_container():
    if 'server' in dir(project.dbconnection):
        assert True
    else:
        assert "_containers.json" in os.listdir(project.temp_dir)


##### load project
project_load = ProjectManager(dbcon, user_id, **{"id": project.id})

@pytest.mark.parametrize("example", [(example_5)])
def test_project_loaded(example):
    assert project_load.name == example["name"]


@pytest.mark.parametrize("example", [example_5])
def test_project_loaded_container_tree(example):
    assert len(project_load.containerTree)==example['asserts']['containers_files_loaded']


@pytest.mark.parametrize("example", [example_5])
def test_table_container(example):
    table = project.getContainerByID(example['asserts']['table_container_ID']).containers[0]
    if table.containerType == 'table':
        for x in table.containers:
            if not x.containerType == 'column':
                assert False
        assert True


def test_clear_test_project():
    project.deleteDownloadedFiles()
    project.deleteUploadedFiles()
    project.deleteAllProjectFiles()
    rmtree(project.temp_dir)
    assert not Path(project.temp_dir).is_dir()

def test_user_projects():
    if not projects_before and len(projects_invoked) == 1:
        assert True
    else:
        assert False
