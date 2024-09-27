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
import streamlit_helper as sf
import datapackage_handling as dh

import SoilPulse_middle as sp
if not 'Package' in dir():
    from frictionless import Package, steps, Pipeline, portals, Catalog
if not "json" in dir():
    import json

st.set_page_config(layout="wide")

if st.button("direct test of url + zip package"):
    import os
    st.write(os.listdir())
    package = Package("catalogue/example_TUBAF.json")
    st.write(package)
    for x in package.resources:
        st.write(x.to_pandas())

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

def set_session(clear = False, logout = False):
    if logout:
        clear = True
    if "selected" not in st.session_state or clear:
        st.session_state.selected = []
    if "expanded" not in st.session_state or clear:
        st.session_state.expanded = []

    if "localproject" not in st.session_state or clear:
        st.session_state.localproject = None

    if "container" not in st.session_state or clear:
        st.session_state.container = None

    if "con" not in st.session_state:
        st.session_state.con = sp._get_DB_connection()
    if "con" in st.session_state and logout:
        del st.session_state.con

    # get projectlist of User
    if "DBprojectlist" not in st.session_state:
        st.session_state.DBprojectlist = sp._getprojects(
            user_id=st.session_state.user_id,
            con=st.session_state.con)
    if "DBprojectlist" in st.session_state and clear:
        del st.session_state.DBprojectlist

    if 'package' not in st.session_state or clear:
        st.session_state.package = Package()
    if 'pipe' not in st.session_state or clear:
        st.session_state.pipe = ""
    if 'counter' not in st.session_state or clear:
        st.session_state.counter = 0

    if clear:
        if logout:
            del st.session_state.user_id
        st.rerun()


set_session()

###########################################
# Frontend imlementation

c1, c2 = st.columns((8, 2), gap="large")

with c2:
    logout = st.button("Logout and restart session.")
    if logout:
        logout = False
        set_session(logout=True)

if not st.session_state.localproject:
    # welcome
    with c1:
        st.title("Welcome to SoilPulse!")
        st.write("Please create a new project or load one from DB.")

        if 'server' not in dir(st.session_state.con):
            st.warning("Can not connect to the global SoilPulse Database! You still can work locally.")

        cpr1, cpr2 = st.columns(2, gap = 'large')

        # dialog to create new project
        with cpr1:
            st.title("New project")
            new_name = st.text_input("Project Name")
            new_doi = st.text_input("Project DOI")
            if st.button(
                "Add Project",
                disabled=new_doi == "" or
                new_name == ""
            ):
                st.session_state.localproject = sp._add_local_project(
                    new_name,
                    new_doi,
                    st.session_state.user_id,
                    con = st.session_state.con)
                st.rerun()


        # Load Project from DB
        with cpr2:
            if not st.session_state.DBprojectlist:
                DB_project_id = None
            else:
                st.title("Load Project from DB")
                DB_project_id = sf._select_project(
                    projectlist = st.session_state.DBprojectlist
                    )
                # load project from DB
                if DB_project_id:
                    if st.button("load project"):
                        st.session_state.localproject = sp._load_project(
                            user_id=st.session_state.user_id,
                            project_id=DB_project_id,
                            con = st.session_state.con
                            )
                        st.rerun()
    st.stop()

# if localproject is selected
else:
    with st.sidebar:
        st.title('You are on the project **"'
                 + st.session_state.localproject.name +
                 '"**')
        dataview = st.toggle("Show project file tree or data tables.")

    with st.sidebar:
        if not dataview:
            st.write('Here are the elements found in your project tree. You can select one and modify it.')
            selected = streamlit_tree_select.tree_select(
                sp._create_tree_from_project(st.session_state.localproject),
                no_cascade=True,
                checked=st.session_state.selected,
                expanded=st.session_state.expanded
                )

                # use session state as work around for single container selection
            if len(selected["checked"]) != len(st.session_state.selected):
                rerun = True
            else:
                rerun = False
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
            if rerun:
                st.rerun()

# Container edit
with c1:
    if not dataview:
        if st.session_state.localproject:
            if not st.session_state.selected:
                st.warning("Please select an element from your project tree.")
            else:
                container = sp._get_container_content(
                    project = st.session_state.localproject,
                    container_id = st.session_state.selected[0]
                    )

                with st.expander("Container Settings", expanded = True):
                    #st.header("")
                    st.session_state.container = sf._mod_container_content(container)
                if container.containerType == 'file':
                    paths = [x.path for x in st.session_state.package.resources]
                    st.write(paths)
                    if container.path in paths:
                        if st.button("remove from dataset"):
                            st.session_state.package.remove_resource(
                                container.name.replace(".csv",""))
                            st.rerun()
                    else:
                        if st.button("add to final dataset"):
                            import frictionless
                            st.session_state.package.add_resource(
                                frictionless.describe(container.path))
                            st.rerun()
    else:
        dh.main()

            #st.json( {'test':'101','mr':'103','bishop':'102'})

            #sf._modify_agrovoc_concept(container)


# # data visualisation
# with c1:
#     if st.session_state.selected and st.session_state.container:

#         # container data visualisation

#         with st.expander("Container Content", expanded = True):
#             if st.session_state.container.crawler:
#                 tables = st.session_state.container.crawler.crawl()
#                 if tables:
#                     for x in tables:
#                         st.data_editor(x)



with c2:
    if st.session_state.localproject:
        if st.button("Switch to another project."):
            set_session(clear=True)
            st.rerun()

        save = st.button("Apply all changes on "+st.session_state.localproject.name+" to local DB")
        if save:
            DB_project_id = sp._update_local_db(
                project=st.session_state.localproject,
                user_id=st.session_state.user_id,
                con=st.session_state.con)
            st.session_state.DBprojectlist = sp._getprojects(
                        user_id=st.session_state.user_id,
                        con=st.session_state.con)
            save = False
            st.rerun()

        if st.button("Reset all changes to "+st.session_state.localproject.name):
            st.session_state.localproject = sp._load_project(
                user_id=st.session_state.user_id,
                project_id=DB_project_id
                )



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






