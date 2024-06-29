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
    st.write(selected)
    if len(selected["checked"]) > 1:
        st.session_state.selected = [x for x in selected["checked"] if x != st.session_state.selected[0]][0:1]
        st.session_state.expanded = selected["expanded"]
        st.experimental_rerun()
    if len(selected["expanded"]) != len(st.session_state.expanded):
        st.session_state.expanded = selected["expanded"]
        st.experimental_rerun()
    else:
        st.session_state.selected = selected["checked"]
        st.session_state.expanded = selected["expanded"]


#    with c1:
#        st.write(container)
    st.write("all DS_printed")

with c1:
    st.write(st.session_state.selected)



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






