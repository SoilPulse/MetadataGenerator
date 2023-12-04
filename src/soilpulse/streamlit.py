# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 09:33:07 2023

@author: Jonas Lenz
"""

import streamlit as st
from get_metadata import *

st.title("SoilPulse Metadata generator")

# start with a given DOI
#doi = "10.14454/FXWS-0523"
#doi = "10.5281/zenodo.6654150"
#doi = "10.5281/zenodo.10210062"
#doi = "10.5281/zenodo.10209718"
#doi = "10.5281/zenodo.10210061"


doi = st.radio(
    label="Enter DOI",
    options = [
        "10.14454/FXWS-0523",
        "10.5281/zenodo.6654150",
        "10.5281/zenodo.10210062",
        "10.5281/zenodo.10209718",
        "10.5281/zenodo.10210061",
        "10.1594/PANGAEA.885492",
        "10.13140/RG.2.2.14231.83365",
        "10.1594/GFZ.TR32.2"
        ]
    )

ra = doi_ra(doi)
st.write("DOI is registered at: "+ra)

if(ra=="DataCite"):
    st.header("Show some DataCite Metadata")
    meta_ra = doi_meta(doi)
    st.write("Data was created by: "+str(meta_ra['data']['attributes']['creators']))
    st.write("Data is titled: "+str(meta_ra['data']['attributes']['titles'][0]['title']))
    dataset_url = meta_ra['data']['attributes']['url']
    st.write("DOI resolves to: "+str(dataset_url))
    
    if ("zenodo.org" in dataset_url):
        zenodo_id = dataset_url.split("/")[-1].split(".")[-1]
        st.header("Retrieving information for Zenodo dataset "+zenodo_id)
        
        response = requests.get("https://zenodo.org/api/deposit/depositions/"+zenodo_id+"/files").json()
        if (type(response) == dict):
            st.write("Data set can not be retrieved.")
        else:
            st.write("Check files to download:")
            download_files = [
#                file['filename'] for file in response if 'zip' in file['filename']
                file['filename'] for file in response if st.toggle(label=file['filename'])
                ]    
                
#            for file in response:
#                if (".zip" in file['filename']):
#                    st.write("The file "+file['filename']+" can be downloaded at:")
#                    st.write("Download-url: https://zenodo.org/records/"+zenodo_id+"/files/"+file['filename']+"?download=1")
#            st.write(download_files)
    else:
        st.write("Not a Zenodo Dataset - up to now not treated.")
else:
    st.write("Not a DataCite DOI - up to now not treated.")
#print(base64.b64decode(response['data']['attributes']['xml']))

    