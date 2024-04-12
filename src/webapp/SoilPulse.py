# -*- coding: utf-8 -*-
"""
Frontend implementation for the SoilPulse Metadata Generator.

Makes use of st.session_state - see this guide:
https://gist.github.com/asehmi/f7e35c3880897fbae92adc7a5315ac0e
It pickles to cache metadata.

@author: Jonas Lenz
"""

import streamlit as st
st.set_page_config(layout="wide")

st.title("Welcome to SoilPulse!")

st.write("SoilPulse allows you to create and maintain metadata for your\
         dataset, so it can be made machine readable.")
st.link_button("Start Generator", "./Metadata_retriever")
st.write("You can also explore and query all datasets, which are made machine\
         readable through SoilPulse. --> See Explorer")
st.link_button("Start Explorer", "./Explorer")

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






