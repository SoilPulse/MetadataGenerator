# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 05:14:24 2024.

@author: JL
"""

import os
import streamlit as st

import pandas as pd
import numpy as np
from soilpulse import db_access as spdb

from soilpulse.project_management import ProjectManager, DatabaseEntryError
import soilpulse.resource_managers.filesystem
import soilpulse.resource_managers.mysql
import soilpulse.resource_managers.xml
import soilpulse.resource_managers.json
from soilpulse.data_publishers import PublisherFactory, DOIdataRetrievalException


def _getprojects(user_id):
    return spdb.DBconnector().getProjectsOfUser(user_id)


def _select_project(projectlist):
    project = st.radio("Select your Project",
                       options = [x for x in projectlist],
                       format_func = lambda x: projectlist[x],
                       index = None
                       )
    return project


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
        st.write("trying to add project "+new_name)
        project = ProjectManager(**example)
        st.write("Got metadata, trying to get Data. This may take some time...")
        project.downloadPublishedFiles()
        project.keepFiles = True
        st.write("Created temporary Project. Please upload to persist your changes.")
        return project
    except Exception as e:
        st.warning(e)


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


def _update_agrovoc_concept_dump():
    """Get the list of all concepts of agrovoc to a local dict and pickle this.

    Agrovoc currently includes < 44000 concepts, so limit of 100000 concepts
    is sufficient.
    the python sparql wrapper is described there:
        https://sparqlwrapper.readthedocs.io/en/latest/main.html#command-line-script
    the agrovoc sparql endpoint with examples there:
        https://agrovoc.fao.org/sparql
    I build upon the example while deleting date infos:
        "Select all concepts added since date X (e.g. 31/12/2020), URI and EN prefLabel."
    """
    from SPARQLWrapper import SPARQLWrapper, JSON
    import pickle

    sparql = SPARQLWrapper(
        "https://agrovoc.fao.org/sparql/"
    )
    sparql.setReturnFormat(JSON)

    sparql.setQuery("""
                    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                    PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#>
                    SELECT ?concept ?label
                    WHERE {
                        ?concept a skos:Concept .
                        OPTIONAL {
                            ?concept skosxl:prefLabel ?xEnLabel .
                            ?xEnLabel skosxl:literalForm ?label .
                            }
                        FILTER(lang(?label) = 'en')
                        }
                    LIMIT 100000
                    """
                    )
    ret = sparql.queryAndConvert()
    with open("agrov.dump", 'wb') as handle:
        pickle.dump(ret, handle, protocol=pickle.HIGHEST_PROTOCOL)


def _get_agrovoc_dump():
    import pickle

    if not os.path.isfile("agrov.dump"):
        _update_agrovoc_concept_dump()
    with open("agrov.dump", 'rb') as handle:
        ret = pickle.load(handle)
    optio = {r["label"]["value"]:
             r["concept"] for r in ret["results"]["bindings"]}
    return optio


def _modify_agrovoc_concept(container):
    optio = _get_agrovoc_dump()
    keys = list(optio.keys())
    if "agrovoc" in container:
        index = keys.index("soil organic matter")
    else:
        index = None
    agrovoc = st.selectbox("AGROVOC label",
                           keys,
                           help="Agrovoc is a controled vocabulary.\
                               By assigning these vocabularies to your\
                               data, a common understanding of the meaning\
                               can be achieved.",
                           index=index,
                           placeholder="Choose an AGROVOC concept.")
    if agrovoc:
        st.write(agrovoc)
        st.write(
            "https://agrovoc.fao.org/browse/agrovoc/en/page/?uri=" +
            optio[agrovoc]["value"])


def _show_container_content(container):
    st.write(container)
    _modify_agrovoc_concept(container)
    pass

def _update_container(container):
    pass


def _reload_container(container):
    pass


def _getprojectofcontainer(container):
    return "your fancy project"


def _get_conceptsofsubcontainers(container):
    # queries actual and all subcontainers for controlled vocabularies
    return ["Soil organic carbon", "Sand"]


def _get_data_for_concept(container, agrovoc):
    # queries actual and all subcontainers for data of controlled vocabularies and their main identifier
    if container == 1:
        data = pd.DataFrame([[2],
                             [1.5],
                             [2.3],
                             [-0.5],
                             [1]],
                            columns=[str(container)])
    else:
        data = pd.DataFrame(np.random.randn(5, 1),
                            columns=[str(container)])
    return data


def _get_projects_by_concept(agrovoc):
    return [2, 3, 4]


def _visualize_data(container, mainID, agrovoc, projects=[]):
    chart_data = _get_data_for_concept(1, "Runoff")
    for x in projects:
        chart_data[str(x)] = _get_data_for_concept(x, "Runoff")[str(x)]
    # chart_data is data got from container
    st.write(chart_data)
    st.write("showing mockup data")
    st.line_chart(chart_data)
    pass


def _update_local_db(project):
    pass


def _reload_local_db(project):
    pass
