# -*- coding: utf-8 -*-
"""
Frontend implementation for the SoilPulse Metadata Generator.

Makes use of st.session_state - see this guide:
https://gist.github.com/asehmi/f7e35c3880897fbae92adc7a5315ac0e
It pickles to cache metadata.

@author: Jonas Lenz
"""

import streamlit as st
import pandas as pd
import requests
import json
import re
import sys
import os
import pickle
import shutil
sys.path.insert(0, './src')
#import soilpulse.resource_management as rm
from soilpulse.resource_management import ResourceManager as rm
from soilpulse.resource_managers.filesystem import *
from soilpulse.resource_managers.mysql import *
from soilpulse.resource_managers.xml import *
from soilpulse.resource_managers.json import *
from soilpulse.data_publishers import *
from soilpulse.metadata_scheme import *
from soilpulse.db_access import EntityKeywordsDB


def _writes_cache(cache_dir):
    if not os.path.isdir("catalogue/"+cache_dir):
        os.mkdir("catalogue/"+cache_dir)
    if not os.path.isdir("catalogue/"+cache_dir+"/data"):
        os.mkdir("catalogue/"+cache_dir+"/data")
    with open("catalogue/"+cache_dir+"/meta", 'wb') as handle:
        pickle.dump(st.session_state.metainf,
                    handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open("catalogue/"+cache_dir+"/meta.json", 'w') as file:
        file.write(json.dumps(st.session_state.metainf))
    st.rerun()
#    st.write("wrote cache")


def _clear_session_state():
    if "metainf" in st.session_state:
        del st.session_state.metainf


def _clear_cache(cache_dir):
    _clear_session_state()
    shutil.rmtree("catalogue/"+cache_dir)
    st.rerun()


def _load_cache(cache_dir):
    with open("catalogue/"+cache_dir+"/meta", 'rb') as handle:
        st.session_state.metainf = pickle.load(handle)
    st.rerun()

# define initial session state
if 'metainf' not in st.session_state:# and\
#    'doi' not in st.session_state.metainf and\
#    'working_title' not in st.session_state.metainf:
    cache_dir = "nocache"
    st.session_state.metainf = {}


# Frontend imlementation

c1, c2 = st.columns((8, 2), gap="large")


with c1:
    st.title("SoilPulse Metadata generator")
    with st.expander(label="**General Metadata**", expanded='doiorg' not in
                     st.session_state.metainf or 'Author' not in
                     st.session_state.metainf):
        st.session_state.metainf['working_title'] = st.text_input(
            label="Here you can prepare your dataset\
                              for machine readability. Do you want to give\
                              it a working title? (This title will not be\
                              recorded in the final metadata.)",
                              value="My data",
                              on_change=_clear_session_state)

    # value/label diff: https://discuss.streamlit.io/t/label-and-values-in-in-selectbox/1436/6
        type_of_dataset = st.radio(
            label=st.session_state.metainf['working_title'] + " has:",
                           options=["a DOI",
                                    "an URL without DOI",
                                    "local dataset"],
                           horizontal=True,
                           on_change=_clear_session_state
                           )


        if (type_of_dataset == "a DOI"):
            st.session_state.metainf['doi'] = st.selectbox(
                label="Enter DOI (will be a text input later on)",
                options=[
                    "10.6094/UNIFR/151460",
                    "10.5281/zenodo.18726",
                    "10.5281/zenodo.6654150",
                    "10.5281/zenodo.10210062",
                    "10.5281/zenodo.10209718",
                    "10.5281/zenodo.10210061",
                    "10.1594/PANGAEA.885492",
                    "10.13140/RG.2.2.14231.83365",
                    "10.1594/GFZ.TR32.2",
                    "10.3390/su152316295"
                    ],
                on_change=_clear_session_state
                )
        elif (type_of_dataset == "an URL without DOI"):
            st.warning("enter URL to dataset will be fully implemented later")
            st.session_state.metainf['doi'] = "NoDOI"
            for inf in ['Title', 'Author', 'Abstract']:
                st.session_state.metainf[inf] = st.text_input(
                label=inf)
            st.write("Data you refer to by url can be treated, but usually miss a\
             clear license, so SoilPulse will offer you to publish your data\
             to a (dedicated) repository, like \
             [Bonares](https://www.bonares.de) or \
             [Zenodo](https://www.zenodo.org).", unsafe_allow_html=True)
        elif (type_of_dataset == "local dataset"):
            st.warning("local dataset will be implemented later")
#    uploaded_files = st.file_uploader("Choose a file",
#                                      accept_multiple_files=True)
#    st.write(uploaded_files)
#    for uploaded_file in uploaded_files:
#        bytes_data = uploaded_file.read()
#        st.write("filename:", uploaded_file.name)
#        st.write(bytes_data)
            st.stop()
        else:
            st.warning("Something went terribly wrong in front end coding,\
             please contact Admins")
            st.stop()

        cache_dir = re.sub('[^A-Za-z0-9]+', '',
                           st.session_state.metainf['doi'] +
                           st.session_state.metainf['working_title'])
        if os.path.isdir("catalogue/"+cache_dir+"/") and\
                "meta" in os.listdir("catalogue/"+cache_dir+"/"):
            cached = True
            st.write("meta present in cache dir")
        else:
            cached = False

        if (type_of_dataset == "a DOI"):
            getra = st.button("Get metadata of this DOI")
        else:
            getra = False
        if getra:
            if not cached:
                _writes_cache(cache_dir)
    #        st.session_state.metainf = ResourceManager(working_title, doi)
    #        st.write("Metadata retrieved.")
    #        st.write("DOI resolves to: http://doi.org/"+doi)
        # @Honza Here the URL from the doi record is needed as string instead of the DOI-link
            st.session_state.metainf['doiorg'] = rm.getRegistrationAgencyOfDOI(
                st.session_state.metainf['doi'], meta=True)[0]
            if ('metainf' in st.session_state and 'doiorg' in st.session_state.metainf):
                if ('RA' in st.session_state.metainf['doiorg']):
                    st.write("DOI is registered at: " +
                             st.session_state.metainf['doiorg']['RA'])
                    if (st.session_state.metainf['doiorg']['RA'] == "DataCite"):
                        st.session_state.metainf['Datacite'] = rm.getDOImetadata(st.session_state.metainf['doi'])
                        dataset_url = str(st.session_state.metainf['Datacite']['data']['attributes']['url'])
                    if ('metainf' in st.session_state and "zenodo.org" in dataset_url):
                        st.session_state.metainf['zenodo_id'] =\
        dataset_url.split("/")[-1].split(".")[-1]
                        response = requests.get(
            "https://zenodo.org/api/deposit/depositions/" +
            st.session_state.metainf['zenodo_id']+"/files"
            ).json()
                        if (type(response) is dict):
                            st.write("We could not identify download links from this ressource (works only for Zenodo by now.)\
                                 But you can still upload files.")
                        else:
                            st.session_state.metainf['ZenodoFiles'] = response
                _writes_cache(cache_dir)

with c1:
    if 'metainf' in st.session_state and\
        'doiorg' in st.session_state.metainf or\
            'Author' in st.session_state.metainf:
        with st.expander(label="**Dataset loader**", expanded=True):
            if ('ZenodoFiles' in st.session_state.metainf):
                st.write("We found files assigned to your record. Please select those to\
                              be loaded:")
            else:
                st.session_state.metainf['ZenodoFiles'] = []
            st.write("You can add download links here:")
            newfilename = st.text_input(label = "Filename",value='filename')
            newURL = st.text_input(label = "URL",value='URL')
            if st.button(label="Add file"):
                st.session_state.metainf['ZenodoFiles'].append({"filename": newfilename,
                                                           "links":{"download": newURL}})

            # dfall = pd.DataFrame(st.session_state.metainf['ZenodoFiles'])
            # df = dfall[["filename"]]
            # df['URL'] = [file['download'] for file in dfall['links']]
            # df.loc[:, "Download (again)?"] = [".zip" in file for file in df["filename"]]
            # df.loc[:, "File loaded"] = [file.replace(".zip", "") in os.listdir(
            #     "catalogue/"+cache_dir+"/data") for file in df["filename"]]

            # edited_df = st.data_editor(df,
            #                            hide_index=True,
            #                            disabled=["File loaded"]
            #                            )

            fis1, fis2, fis3, fis4 = st.columns((3,3,1,1))
            with fis1:
                st.write('Filename')
            with fis2:
                st.write('URL')
            with fis3:
                st.write("Download?")
            with fis4:
                st.write("File loaded")
            i = 0
            for fileno in st.session_state.metainf['ZenodoFiles']:
                i += 1
                with fis1:
                    fileno['filename'] = st.text_input(
                        value=fileno['filename'],
                        label=" ",
                        key="name"+str(i))
                with fis2:
                    fileno['links']['download'] = st.text_input(
                        value=fileno['links']['download'],
                        label=" ",
                        key="URL"+str(i))
                with fis4:
                    st.write("")
                    fileno['loaded'] = st.checkbox(
                        label=" ",
                        key="loaded"+str(i),
                        value=fileno['filename'] in os.listdir(
                            "catalogue/"+cache_dir+"/data")
                        )
                    st.write("")
                    st.write("")
                with fis3:
                    st.write("")
                    fileno['download'] = st.checkbox(
                        label=" ",
                        key="load"+str(i),
                        value=".zip" in fileno['filename'])
                    st.write("")
                    st.write("")


            getFiles = st.button("Download selected files")
            if getFiles:
                st.session_state.metainf['containerTree'] = []
#                download_files = edited_df.loc[
#                    edited_df.loc[:, "Download (again)?"],["filename", "URL"]].to_dict(orient="records")
                st.write("downloading - may take a while:")
#                st.write(download_files)
                
                res = rm.downloadPublishedFiles(
                    st.session_state.metainf,
                    "catalogue/"+cache_dir+"/data/")


            #set_downloadfiles(RM.available_files()) # set bool list to filter available files
            #    RM.download_files()



with c2:
    st.title("Metadata map")
    if cached:
        st.warning("Such a dataset was allready in progress. Reload metadata?")
        if st.button("Load cache"):
            _load_cache(cache_dir)
        if st.button(":red[Clear cache]"):
            _clear_cache(cache_dir)
    if "metainf" in st.session_state:
        if st.button(":green[Write cache]"):
            _writes_cache(cache_dir)
#        if st.button(":red[Clear inputs]"):
#            _clear_session_state()
#        st.download_button(label="Download metadata.",
#                           data=json.dumps(st.session_state.metainf),
#                           file_name=st.session_state['working_title']+".soilpulse")
        show_meta = st.toggle(label="Show Metadata of " +
                              st.session_state.metainf['working_title'],
                              value=False)
        if show_meta:
            st.json(st.session_state.metainf)

