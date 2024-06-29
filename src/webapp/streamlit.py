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


# Frontend imlementation

c1, c2 = st.columns((8, 3), gap="large")


with st.sidebar:
    new_ds_dialog = st.checkbox("Add Dataset Dialog")

# show trees of all Datasets
    for dataset in sp._get__local_datasets():
        streamlit_tree_select.tree_select(
            sp._create_tree(dataset)
            )
    st.write("all DS_printed")


if new_ds_dialog:
    with c1:
        dia1, dia2, dia3 = st.columns(3)
        with dia1:
            st.session_state['new_name'] = st.text_input("Dataset Name")
        with dia2:
            st.session_state['new_doi'] = st.text_input("Dataset DOI")
        with dia3:
            st.button(
                "Add Dataset",
                on_click=sp._add_dataset(
                    st.session_state['new_doi'],
                    st.session_state['new_name']),
                disabled=st.session_state['new_doi'] == "" or
                         st.session_state['new_name'] == ""
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
# webapp gets the Datasets definition from ResourceManager

# Resource and dataset editing page is displayed (container tree, datasets, Resource's metadata entities)
# here should be available options for manipulating the datasets
    # add/edit/remove Resource's metadata entities
    # create Dataset
    # delete Dataset
    # edit Dataset properties (change name, description etc.)
    # add containers (files, tables ...) to Dataset
    # remove containers






