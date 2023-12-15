# -*- coding: utf-8 -*-
"""
Frontend implementation for the SoilPulse Metadata Generator.

Crawls the dataset files.
Makes use of st.session_state - see this guide:
https://gist.github.com/asehmi/f7e35c3880897fbae92adc7a5315ac0e
It pickles to cache metadata.

@author: Jonas Lenz
"""

import streamlit as st
import requests
import pickle
# import shutil
import os
import pandas as pd
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

if 'metainf' in st.session_state and 'doiorg' in st.session_state['metainf']:
    st.write(str("Here you can crawl the dataset files of the dataset **" +
             st.session_state['metainf']['doiorg']['DOI'] +
             "** to generate and complete metadata"))
    cache_dir = re.sub('[^A-Za-z0-9]+', '',
                       st.session_state['metainf']['doiorg']['DOI'])
else:
    st.write("Please go back to Metadata retriever first to select dataset.")
    st.link_button("Start Generator", "./Metadata_retriever")
#    st.write("Or start over by providing a link/lokal path to\
#             prepare a data publication.")
#    st.textbox("paste URL/path to dataset")

if ('metainf' in st.session_state and
        'ZenodoFiles' in st.session_state.metainf):
    # ## Test with editable pandas dataframe
    df = pd.DataFrame(st.session_state.metainf['ZenodoFiles'])
    df = df.drop(columns=["id", "filesize", "checksum", "links"])
    df["Download (again)?"] = [".zip" in file for file in df["filename"]]
    df["File loaded"] = [file in os.listdir("catalogue/"+cache_dir)
                         for file in df["filename"]]
    edited_df = st.data_editor(df,
                               hide_index=True,
                               disabled=["filename", "File loaded"]
                               )
    download_files2 = edited_df.loc[edited_df["Download (again)?"]]["filename"]
    st.write(download_files2)

    # first shot on file selector
    st.write("Check files to download:")
    download_files = [
        file['filename']
        for file in st.session_state.metainf['ZenodoFiles']
        if st.toggle(label=file['filename'],
                     value=".zip" in file['filename'])
        ]
    st.write(download_files)
    getZenodoFiles = st.button("Download selected Zenodo files")
    if getZenodoFiles:
        for file in download_files:
            url = str("https://zenodo.org/records/" +
                      st.session_state.metainf['zenodo_id'] +
                      "/files/" + file)
            response = requests.get(url, params={"download": "1"})
            st.write(response.url)
            if response.ok:
                with open("catalogue/"+cache_dir+"/"+file,
                          mode="wb") as filesave:
                    filesave.write(response.content)
            # print(base64.b64decode(response['data']['attributes']['xml']))


if "metainf" in st.session_state:
    st.write("You can cache the retrieved metadata now:")
    st.json(st.session_state.metainf)
    write_cache = st.button(":green[Write cache]", on_click=_writes_cache)
