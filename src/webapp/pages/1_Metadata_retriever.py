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
import shutil
import os
import sys
import re
sys.path.insert(0, './src/soilpulse')
import get_metadata as gm
# from soilpulse import get_metadata as gm


def _writes_cache():
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

st.write("Here you can prepare your dataset for machine readability.")
st.write("You can start by selecting (will be a textbox later) a DOI:")

doi = st.selectbox(
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
    # index=None, # start without preselected DOI -> needs further adaption.
    # placeholder="Select DOI...",
    on_change=_clear_session_state
    )

load_cache = False

cache_dir = re.sub('[^A-Za-z0-9]+', '', doi)
if os.path.isdir("catalogue/"+cache_dir) and\
  "meta" in os.listdir("catalogue/"+cache_dir):
    st.write("The metadat of this dataset is allready in the cache.")
    clear_cache = st.button(":red[Clear cache]")
    load_cache = st.button("Load cache")
    if (clear_cache):
        shutil.rmtree("catalogue/"+cache_dir)
        st.rerun()

if (load_cache):
    with open("catalogue/"+cache_dir+"/meta", 'rb') as handle:
        st.session_state.metainf = pickle.load(handle)

st.header("Retrieve metadata")
getra = st.button("Get doi.org metadata")
if getra:
    st.session_state.metainf = {}
    st.session_state.metainf['doiorg'] = gm.doi_ra(doi, meta=True)[0]
if ('metainf' in st.session_state and 'doiorg' in st.session_state.metainf):
    if ('RA' in st.session_state.metainf['doiorg']):
        st.write("DOI is registered at: " +
                 st.session_state.metainf['doiorg']['RA'])

        if (st.session_state.metainf['doiorg']['RA'] == "DataCite"):

            getDatacite = st.button("Get DataCite Metadata")
            if getDatacite:
                st.session_state.metainf['Datacite'] = gm.doi_meta(doi)

if ('metainf' in st.session_state and 'Datacite' in st.session_state.metainf):
    st.write("Data was created by:"
             + str(st.session_state.metainf
                   ['Datacite']['data']['attributes']['creators']))
    st.write("Data is titled: "
             + str(st.session_state.
                   metainf['Datacite']['data']
                   ['attributes']['titles'][0]['title']))
    dataset_url = str(st.session_state.
                      metainf['Datacite']['data']
                      ['attributes']['url'])
    st.write("DOI resolves to: "+str(dataset_url))
else:
    st.write("Not a DataCite DOI - up to now not treated.")

if ('metainf' in st.session_state and "zenodo.org" in dataset_url):
    st.session_state.metainf['zenodo_id'] =\
        dataset_url.split("/")[-1].split(".")[-1]
    st.header("Retrieving information for Zenodo dataset " +
              st.session_state.metainf['zenodo_id'])

    getZenodo = st.button("Get Zenodo file list")
    if getZenodo:
        response = requests.get(
            "https://zenodo.org/api/deposit/depositions/" +
            st.session_state.metainf['zenodo_id']+"/files"
            ).json()
        if (type(response) is dict):
            st.write("Data set can not be retrieved.")
        else:
            st.session_state.metainf['ZenodoFiles'] = response
    else:
        st.write("Not a Zenodo Dataset - up to now not treated.")


if "metainf" in st.session_state:
    st.write("You can cache the retrieved metadata now:")
    st.json(st.session_state.metainf)
    write_cache = st.button(":green[Write cache]", on_click=_writes_cache)
