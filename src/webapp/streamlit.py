# -*- coding: utf-8 -*-
"""
Frontend implementation for the SoilPulse Metadata Generator.

Makes use of st.session_state - see this guide:
https://gist.github.com/asehmi/f7e35c3880897fbae92adc7a5315ac0e
It pickles to cache metadata.

@author: Jonas Lenz
"""

import streamlit as st
import requests
import pickle
import os
import re
from soilpulse import get_metadata as gm


def _writes_cache():
    with open("instance/"+cache_file, 'wb') as handle:
        pickle.dump(st.session_state.metainf,
                    handle, protocol=pickle.HIGHEST_PROTOCOL)
#    import json
#    with open('instance/file.txt', 'w') as file:
#        file.write(json.dumps(st.session_state.metainf))


def _clear_session_state(prop):
    if prop in st.session_state:
        del st.session_state[prop]


st.title("SoilPulse Metadata generator")

doi = st.radio(
    label="Enter DOI",
    options=[
        "10.14454/FXWS-0523",
        "10.5281/zenodo.6654150",
        "10.5281/zenodo.10210062",
        "10.5281/zenodo.10209718",
        "10.5281/zenodo.10210061",
        "10.1594/PANGAEA.885492",
        "10.13140/RG.2.2.14231.83365",
        "10.1594/GFZ.TR32.2",
        "10.3390/su152316295"
        ],
    on_change=_clear_session_state,
    args="metainf"
    )

load_cache = False

cache_file = re.sub('[^A-Za-z0-9]+', '', doi)
if cache_file in os.listdir("instance"):
    st.write("The metadat of this dataset is allready in the cache.")
    clear_cache = st.button(":red[Clear cache]")
    load_cache = st.button("Load cache")
    if (clear_cache):
        os.unlink("instance/"+cache_file)
        st.rerun()

if (load_cache):
    with open("instance/"+cache_file, 'rb') as handle:
        st.session_state.metainf = pickle.load(handle)

st.header("Retrieve metadata")
getra = st.button("Get RA")
if getra:
    st.session_state.metainf = {}
    st.session_state.metainf['ra'] = gm.doi_ra(doi)
if ('metainf' in st.session_state):
    if ('ra' in st.session_state.metainf):
        st.write("DOI is registered at: "+st.session_state.metainf['ra'])

        if (st.session_state.metainf['ra'] == "DataCite"):
            st.header("Show some DataCite Metadata")
            meta_ra = gm.doi_meta(doi)
            st.write("Data was created by:"
                     + str(meta_ra['data']['attributes']['creators']))
            st.write("Data is titled: "
                     + str(meta_ra['data']['attributes']['titles'][0]['title']))
            dataset_url = meta_ra['data']['attributes']['url']
            st.write("DOI resolves to: "+str(dataset_url))

            if ("zenodo.org" in dataset_url):
                zenodo_id = dataset_url.split("/")[-1].split(".")[-1]
                st.header("Retrieving information for Zenodo dataset "+zenodo_id)

                response = requests.get(
                    "https://zenodo.org/api/deposit/depositions/"+zenodo_id+"/files"
                    ).json()
                if (type(response) is dict):
                    st.write("Data set can not be retrieved.")
                else:
                    st.write("Check files to download:")
                    download_files = [
                        file['filename']
                        for file in response
                        if st.toggle(label=file['filename'])
                        ]

#            for file in response:
#                if (".zip" in file['filename']):
#                    st.write("The file "+file['filename']+
#                             " can be downloaded at:")
#                    st.write("Download-url: https://zenodo.org/records/"
#                       + zenodo_id+"/files/"+file['filename']+"?download=1")
#            st.write(download_files)
            else:
                st.write("Not a Zenodo Dataset - up to now not treated.")
        else:
            st.write("Not a DataCite DOI - up to now not treated.")
        # print(base64.b64decode(response['data']['attributes']['xml']))

if "metainf" in st.session_state:
    st.write("You can cache the retrieved metadata now:")
    st.json(st.session_state.metainf)
    write_cache = st.button(":green[Write cache]", on_click=_writes_cache)
