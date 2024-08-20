# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 05:14:24 2024.

@author: JL
"""

from soilpulse import db_access as spdb

from soilpulse.project_management import ProjectManager, DatabaseEntryError
import soilpulse.resource_managers.filesystem
import soilpulse.resource_managers.mysql
import soilpulse.resource_managers.xml
import soilpulse.resource_managers.json
from soilpulse.data_publishers import PublisherFactory, DOIdataRetrievalException


def _getprojects(user_id):
    try:
        DBprojectlist = spdb.DBconnector().getProjectsOfUser(user_id)
    except:
        DBprojectlist = None
    return DBprojectlist



def _load_project(user_id, project_id):
    example = {"user_id": user_id, "id" : project_id}
    project = ProjectManager(**example)
#    project.dbconnection = spdb.DBconnector()
#    project.dbconnection.loadProject(project)
    return project


def _add_local_project(new_name, new_doi, user_id):
    example = {"name": new_name,
               "doi": new_doi,
               "user_id" : user_id,
               "id" : "local"}

    #todo - add precheck, if DOI could be valid to not spam doi.org

    try:
#        st.write("trying to add project "+new_name)
        project = ProjectManager(**example)
#        st.write("Got metadata, trying to get Data. This may take some time...")
        project.downloadPublishedFiles()
        project.keepFiles = True
#        st.write("Created temporary Project. Please upload to persist your changes.")
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





def _update_local_db(project, user_id):
    project.dbconnection = spdb.DBconnector()
    if project.id == 'local':
        project.id = project.dbconnection.establishProjectRecord(user_id, project)

    project.updateDBrecord()
    return project.id
