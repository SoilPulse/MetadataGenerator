# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 05:14:24 2024.

@author: JL
"""

from soilpulse import db_access as spdb

from soilpulse.project_management import ProjectManager, DatabaseEntryError, SourceFile
import soilpulse.resource_managers.filesystem
import soilpulse.resource_managers.mysql
import soilpulse.resource_managers.xml
import soilpulse.resource_managers.json
from soilpulse.data_publishers import PublisherFactory, DOIdataRetrievalException

from pathlib import Path
import os

project_files_dir_name = "catalogue"
project_files_root = Path(os.path.join(project_files_dir_name))
project_files_root.mkdir(parents=True, exist_ok=True)

def _get_DB_connection(rootdir=project_files_root):
    return spdb.NullConnector(rootdir)

def _getprojects(user_id, con):
    try:
        DBprojectlist = con.getProjectsOfUser(user_id)
    except:
        DBprojectlist = None
    return DBprojectlist



def _load_project(user_id, project_id, con):
    example = {"id": project_id}
    project = ProjectManager(con, user_id, **example)
    return project


def _add_local_project(new_name, new_doi, new_url, user_id, con):
    example = {"name": new_name,
               "doi": new_doi}

    #todo - add precheck, if DOI could be valid to not spam doi.org

    try:

        project = ProjectManager(con, user_id, **example)
#        st.write("trying to add project "+new_name)
#        st.write("Got metadata, trying to get Data. This may take some time...")
        if new_url:
            project.publishedFiles= [SourceFile(id = 1, filename = "referencedfile", source_url = new_url)]
        project.downloadPublishedFiles()
        project.keepFiles = True
#        st.write("Created temporary Project. Please upload to persist your changes.")
        _update_local_db(project, user_id, con)
        return project
    except Exception as e:
        raise e
#        st.warning(e)


def _create_tree_from_project(project):
    projecttree = project.containerTree
    tree = _create_tree_from_container(projecttree)
    return tree


def _create_tree_from_container(projecttree):
    tree_dict = []
    for container in projecttree:

        if len(container.containers)==0:
            tree_dict.append(
                {
                    "label": container.name,
                    "value": container.id
                    }
                )
        else:
            tree_dict.append(
                {
                    "label": container.name,
                    "value": container.id,
                    "children": _create_tree_from_container(container.containers)
                    }
                )
    return tree_dict



def _get_container_content(project, container_id):
    return project.getContainerByID(int(container_id))


def _get_conceptsofsubcontainers(container):
    # queries actual and all subcontainers for controlled vocabularies
    return ["Soil organic carbon", "Sand"]


def _get_projects_by_concept(agrovoc):
    return [2, 3, 4]


def _update_local_db(project, user_id, con):
    project.updateDBrecord(con)
    return project.id
