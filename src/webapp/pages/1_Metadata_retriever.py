# -*- coding: utf-8 -*-
"""
Frontend implementation for the SoilPulse Metadata Generator.

Makes use of st.session_state - see this guide:
https://gist.github.com/asehmi/f7e35c3880897fbae92adc7a5315ac0e
It pickles to cache metadata.

@author: Jonas Lenz
"""

import streamlit as st
import re
import sys
import os
import pickle
import shutil
sys.path.insert(0, './src')
#import soilpulse.resource_management as rm
from soilpulse.resource_management import ResourceManager

# following imports should be obsolete later on
from soilpulse.resource_managers.filesystem import *
from soilpulse.resource_managers.mysql import *
from soilpulse.resource_managers.xml import *
from soilpulse.resource_managers.json import *
from soilpulse.data_publishers import *
from soilpulse.metadata_scheme import *
from soilpulse.db_access import EntityKeywordsDB


def _writes_cache(cache_dir="cache"):
    if not os.path.isdir("catalogue/"+cache_dir):
        os.mkdir("catalogue/"+cache_dir)
    with open("catalogue/"+cache_dir+"/meta", 'wb') as handle:
        pickle.dump(st.session_state.metainf,
                    handle, protocol=pickle.HIGHEST_PROTOCOL)
#    import json
#    with open('catalogue/file.txt', 'w') as file:
#        file.write(json.dumps(st.session_state.metainf))


def _clear_session_state():
    if "metainf" in st.session_state:
        del st.session_state["metainf"]


st.title("SoilPulse Metadata generator")

working_title = st.text_input(label="Here you can prepare your dataset\
                              for machine readability. Do you want to give\
                              it a working title? (This title will not be\
                              recorded in the final metadata.)",
                              value="My fancy dataset to be made reusable")

# st.write("You can start by selecting (will be a textbox later) a DOI:")
type_of_dataset = st.radio(label=working_title + " has:",
                           options=["a DOI",
                                    "an URL without DOI",
                                    "no online ressource, only local dataset"],
                           horizontal=True
                           )

if (type_of_dataset == "a DOI"):
    doi = st.selectbox(
        label="Enter DOI (will be a text input later on)",
        options=[
            "10.5281/zenodo.18726",
            "10.5281/zenodo.6654150",
            "10.5281/zenodo.10210062",
            "10.5281/zenodo.10209718",
            "10.5281/zenodo.10210061",
            "10.1594/PANGAEA.885492",
            "10.13140/RG.2.2.14231.83365",
            "10.1594/GFZ.TR32.2",
            "10.3390/su152316295",
            "10.14454/FXWS-0523"
            ],
        on_change=_clear_session_state
        )
elif (type_of_dataset == "an URL without DOI"):
    st.warning("enter URL to dataset will be implemented later")
    st.write("Data you refer to by url can be treated, but usually miss a\
             clear license, so SoilPulse will offer you to publish your data\
             to a (dedicated) repository, like \
             [Bonares](https://www.bonares.de) or \
             [Zenodo](https://www.zenodo.org).", unsafe_allow_html=True)
    st.stop()
elif (type_of_dataset == "no online ressource, only local dataset"):
    st.warning("local dataset will be implemented later")
#    uploaded_files = st.file_uploader("Choose a file",
#                                      accept_multiple_files=True)
#    st.write(uploaded_files)
#    for uploaded_file in uploaded_files:
#        bytes_data = uploaded_file.read()
#        st.write("filename:", uploaded_file.name)
#        st.write(bytes_data)
    st.write("Data you upload can be treated, but usually miss a\
             clear license, so SoilPulse will offer you to publish your data\
             to a (dedicated) repository, like \
             [Bonares](https://www.bonares.de) or \
             [Zenodo](https://www.zenodo.org).", unsafe_allow_html=True)
    st.stop()
else:
    st.warning("Something went terribly wrong in front end coding,\
             please contact Admins")
    st.stop()

#load_cache = False

#if os.path.isdir("catalogue/"+cache_dir) and\
#  "meta" in os.listdir("catalogue/"+cache_dir):
#    st.write("The metadata of this dataset is allready in the cache.")
#    clear_cache = st.button(":red[Clear cache]")
#    load_cache = st.button("Load cache")
#    if (clear_cache):
#        shutil.rmtree("catalogue/"+cache_dir)
#        st.rerun()

#if (load_cache):
#    with open("catalogue/"+cache_dir+"/meta", 'rb') as handle:
#        st.session_state.metainf = pickle.load(handle)


st.header("Retrieve metadata")
getra = st.button("Get metadata of this DOI")
if getra:
    st.session_state.metainf = ResourceManager(working_title, doi)
    st.write("Metadata retrieved.")
    st.write("DOI resolves to: http://doi.org/"+doi)
    # @Honza Here the URL from the doi record is needed as string instead of the DOI-link

    try:
        available_files = st.session_state.metainf.available_files()
        # @Honza here I need a pandas Dataframe wit
    except:
        available_files = False
        st.write("We could not identify download links from this ressource.\
                 But you can still upload files.")
    if available_files:
        st.header("We found files assigned to your DOI. Please select those to\
                  be loaded:")

    # ## Test with editable pandas dataframe
    # @Honza get file info available from repository. -
    def set_downloadfiles():
        # I want to show a dataframe where the user can define which files to
        # download and which are allready loaded
        dfall = pd.DataFrame(st.session_state.metainf['ZenodoFiles']['entries'])
        df = dfall[["key"]]
        df['URL'] = [file['content'] for file in dfall['links']]
        df["Download (again)?"] = [".zip" in file for file in df["key"]]
        df["File loaded"] = [file.replace(".zip", "") in os.listdir(
            "catalogue/"+cache_dir+"/data") for file in df["key"]]
        edited_df = st.data_editor(df,
                                   hide_index=True,
                                   disabled=["key", "File loaded"]
                                   )
        download_files = edited_df.loc[
            edited_df["Download (again)?"]]["key"].tolist()
        #    st.write(download_files)
    set_downloadfiles(RM.available_files()) # set bool list to filter available files
#    RM.download_files()

    with st.expander("Show Metadata", expanded=False):
        st.json(st.session_state.metainf.json())
        # @Honza I would like to show here all up to then retrieved metadata, parsed as json.
        # and inform users about missing registrations of data platforms/RAs/whatever
        RAbool = st.button("dummy bool, if RA is registered.")
        if True:
            st.write("RA:")
        else:
            st.warning("<RA> not registered at SoilPulse.")
            rqRA = st.button("Request the team to add <RA>.")
            if rqRA:
                def _opengitissue(ra="<RA>"):
                    pass


if "metainf" in st.session_state:
    st.write("You can cache the retrieved metadata now on the server:")
    # @Honza - push it to the server for persistance beyond the actual session?
    write_cache = st.button(":green[Write cache]", on_click=_writes_cache)
    st.write("You can download your current state of metadata treatment and\
             resume later with this file.")
    st.download_button(label="Take a rest from metadataing.",
                       data=st.session_state.metainf.json().to_csv(),
                       file_name=working_title+".soilpulse")
