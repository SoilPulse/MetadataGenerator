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


# use session state as work around for single container selection
# https://github.com/Schluca/streamlit_tree_select/issues/1#issuecomment-1554552554

if "selected" not in st.session_state:
    st.session_state.selected = []
if "expanded" not in st.session_state:
    st.session_state.expanded = []

# Frontend imlementation

c1, c2 = st.columns((8, 3), gap="large")


with st.sidebar:
    with st.expander("Add dataset"):
        st.session_state['new_name'] = st.text_input("Dataset Name")
        st.session_state['new_doi'] = st.text_input("Dataset DOI")
        if st.button(
            "Add Dataset",
            disabled=st.session_state['new_doi'] == "" or
            st.session_state['new_name'] == ""
        ):
            sp._add_dataset(
                st.session_state['new_doi'],
                st.session_state['new_name'])

# show trees of all Datasets
with st.sidebar:
    selected = streamlit_tree_select.tree_select(
        sp._create_tree("./catalogue/"),
        no_cascade=True,
        checked=st.session_state.selected,
        expanded=st.session_state.expanded
        )
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
    dataset = sp._getdatasetofcontainer(st.session_state.selected)


with c1:
    with st.container():
        sp._show_container_content(st.session_state.selected)
        if st.button("Save Changes for this container locally"):
            sp._update_container(st.session_state.selected)
        if st.button("Reset changes on this container"):
            sp._reload_container(st.session_state.selected)
    with st.container():
        # get agrovoc concepts in container for selection of visualisation target
        agrovoc = ["Corg", "Bulk"]
        mainID = "experiment ID"
        if st.button("Show context of other datasets"):
            sp._visualize_data(st.session_state.selected, mainID, agrovoc, alldatsets = True)
        else:
            sp._visualize_data(st.session_state.selected, mainID, agrovoc)

with c2:
    if st.button("Apply all changes on "+dataset+" to local DB"):
        sp._update_local_db(dataset)
    if st.button("Reset all changes to "+dataset):
        sp._reload_local_db(dataset)


# here the starting point options should be available:
# and does action according to option selected in the first step
    # 1) establish new ResourceManager by uploading files ("drag files here to upload them")
        # -> upload the files to the tempDir, unpack archives if any, recognize file structure (establish container tree)
    # 2) establish new ResourceManager by providing URL to download files (text box for pasting the url)
        # -> download the files to the tempDir, unpack archives if any, recognize file structure (establish container tree)
    # 3) open existing ResourceManager from record saved in SoilPulse DB
        # -> re-establish Resource from state saved in resource metadata mappings database

# webapp gets the container tree from ResourceManager
# webapp gets the Datasets definition from ResourceManager

# Resource and dataset editing page is displayed (container tree, datasets, Resource's metadata entities)
# here should be available options for manipulating the datasets
    # add/edit/remove Resource's metadata entities
    # create Dataset
    # delete Dataset
    # edit Dataset properties (change name, description etc.)
    # add containers (files, tables ...) to Dataset
    # remove containers






