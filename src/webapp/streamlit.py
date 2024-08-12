# -*- coding: utf-8 -*-
"""
Frontend implementation for the SoilPulse Metadata Generator.

Makes use of st.session_state - see this guide:
https://gist.github.com/asehmi/f7e35c3880897fbae92adc7a5315ac0e
It pickles to cache metadata.

@author: Jonas Lenz
"""

import streamlit as st
import streamlit_tree_select

import SoilPulse_middle as sp

st.set_page_config(layout="wide")


#### Mockup login page
if "user_id" not in st.session_state:
    st.title("Welcome to SoilPulse")
    st.write("Here you can make your new data or any legacy dataset FAIR.")
    st.write("")
    if st.button("Login as Demo User"):
        st.session_state.user_id = 1
        st.rerun()
    else:
        st.stop()


#### Set session states

# use session state as work around for single container selection
# https://github.com/Schluca/streamlit_tree_select/issues/1#issuecomment-1554552554

if "selected" not in st.session_state:
    st.session_state.selected = []
if "expanded" not in st.session_state:
    st.session_state.expanded = []


# get projectlist of User
if "projectlist" not in st.session_state:
    try:
        st.session_state.projectlist = sp._getprojects(st.session_state.user_id)
    except:
        with st.sidebar:
            st.warning("Can not connect to SoilPulse Database! You still can work locally.")
        st.session_state.projectlist = None



###########################################
# Frontend imlementation

c1, c2 = st.columns((8, 3), gap="large")


# welcome
with st.sidebar:
    st.title("Welcome to SoilPulse!")

# dialog to create new project
with st.sidebar:
    with st.expander("Add project"):
        st.session_state['new_name'] = st.text_input("Project Name")
        st.session_state['new_doi'] = st.text_input("Project DOI")
        if st.button(
            "Add Project",
            disabled=st.session_state['new_doi'] == "" or
            st.session_state['new_name'] == ""
        ):
            sp._add_project(
                st.session_state['new_doi'],
                st.session_state['new_name'])

# select Project
with st.sidebar:
    if st.session_state.projectlist:
        with st.expander("Select Project", expanded = True):
            project_id = sp._select_project(
                projectlist = st.session_state.projectlist
                )
    else:
        project_id = None


    # load project from DB
    if project_id:
        if st.button("load project"):
            st.session_state.project = sp._load_project(
                user_id=st.session_state.user_id,
                project_id=project_id
                )


if "project" in st.session_state:
# show tree of Project
    with st.sidebar:
        selected = streamlit_tree_select.tree_select(
            sp._create_tree_from_project(st.session_state.project),
            no_cascade=True,
            checked=st.session_state.selected,
            expanded=st.session_state.expanded
            )

            # use session state as work around for single container selection
        if len(selected["checked"]) > 1:
            st.session_state.selected = [x for x in selected["checked"] if x != st.session_state.selected[0]][0:1]
            st.session_state.expanded = selected["expanded"]
            st.rerun()
        elif len(selected["expanded"]) != len(st.session_state.expanded):
            st.session_state.expanded = selected["expanded"]
            st.rerun()
        else:
            st.session_state.selected = selected["checked"]
            st.session_state.expanded = selected["expanded"]


with c1:
    if project_id:
        st.write("On Project:" + st.session_state.projectlist[project_id])
    # container editing
    with st.container(border = True):
        st.header("Container Settings")
        sp._show_container_content(st.session_state.selected)
        if st.button("Save Changes for this container locally"):
            sp._update_container(st.session_state.selected)
        if st.button("Reset changes on this container"):
            sp._reload_container(st.session_state.selected)

    # container data visualisation
    with st.container(border = True):
        st.header("Included Data")
        # get agrovoc concepts in container for selection of visualisation target
        agrovoc = ["Corg", "Bulk"]
        mainID = "experiment ID"
        projects = st.multiselect(
            "Concept availble in",
            options=sp._get_projects_by_concept("agrovoc"),
            )
        sp._visualize_data(st.session_state.selected, mainID, agrovoc, projects)


    with c2:
        if st.button("Apply all changes on "+st.session_state.projectlist[project_id]+" to local DB"):
            sp._update_local_db(project_id)
        if st.button("Reset all changes to "+st.session_state.projectlist[project_id]):
            sp._reload_local_db(project_id)


# here the starting point options should be available:
# and does action according to option selected in the first step
    # 1) establish new ResourceManager by uploading files ("drag files here to upload them")
        # -> upload the files to the tempDir, unpack archives if any, recognize file structure (establish container tree)
    # 2) establish new ResourceManager by providing URL to download files (text box for pasting the url)
        # -> download the files to the tempDir, unpack archives if any, recognize file structure (establish container tree)
    # 3) open existing ResourceManager from record saved in SoilPulse DB
        # -> re-establish Resource from state saved in resource metadata mappings database

# webapp gets the container tree from ResourceManager
# webapp gets the Projects definition from ResourceManager

# Resource and project editing page is displayed (container tree, projects, Resource's metadata entities)
# here should be available options for manipulating the projects
    # add/edit/remove Resource's metadata entities
    # create Project
    # delete Project
    # edit Project properties (change name, description etc.)
    # add containers (files, tables ...) to Project
    # remove containers






