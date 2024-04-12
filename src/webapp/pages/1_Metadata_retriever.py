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
import copy

import streamlit_tree_select

import tree3
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
#        file.write(json.dumps(st.session_state.metainf))
# this is a quick fix - shall be really fixed with merging to Backend
        file.write(json.dumps(
            {k:v for k,v in st.session_state.metainf.items() if k != 'containerTree'}
            ))
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
    if not os.path.isdir("catalogue/"+cache_dir+"/data"):
        os.mkdir("catalogue/"+cache_dir+"/data")
    st.rerun()


# define initial session state
if 'metainf' not in st.session_state:  # and\
    # 'doi' not in st.session_state.metainf and\
    # 'working_title' not in st.session_state.metainf:
    cache_dir = "nocache"
    st.session_state.metainf = {}


# Frontend imlementation

c1, c2 = st.columns((8, 3), gap="large")


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
                     "a local dataset"],
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
        elif (type_of_dataset == "a local dataset"):
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
                           st.session_state.metainf['doi'])
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
                    if ('metainf' in st.session_state and
                            "zenodo.org" in dataset_url):
                        st.session_state.metainf['zenodo_id'] =\
                            dataset_url.split("/")[-1].split(".")[-1]
                        response = requests.get(
                            "https://zenodo.org/api/deposit/depositions/" +
                            st.session_state.metainf['zenodo_id']+"/files"
                            ).json()
                        if (type(response) is dict):
                            st.write(
                                "We could not identify download links from\
                                    this ressource (works only for Zenodo by\
                                    now.) But you can still upload files.")
                        else:
                            st.session_state.metainf['ZenodoFiles'] = response

with c1:
    if 'metainf' in st.session_state and\
        'doiorg' in st.session_state.metainf or\
            'Author' in st.session_state.metainf:
        with st.expander(label="**Dataset loader**", expanded=True):
            if ('ZenodoFiles' in st.session_state.metainf):
                st.write("We found files assigned to your record.\
                         Please select those to be loaded:")
            else:
                st.session_state.metainf['ZenodoFiles'] = []
            st.write("You can add download links here:")
            newfilename = st.text_input(label="Filename", value='filename')
            newURL = st.text_input(label="URL", value='URL')
            if st.button(label="Add file"):
                st.session_state.metainf['ZenodoFiles'].append(
                    {"filename": newfilename, "links": {"download": newURL}})

            fis1, fis2, fis3, fis4 = st.columns((3, 3, 1, 1))
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
                st.write("You can proceed to explain your files.")


if 'doiorg' in st.session_state.metainf and cached and \
        os.path.isdir("catalogue/"+cache_dir+"/data/"):
    if len(os.listdir("catalogue/"+cache_dir+"/data/")) > 0:
        with st.sidebar:
            rufl1, rufl2 = st.columns(2)
            with rufl1:
                rfl = st.button("refresh file list")
            with rufl2:
                ufl = st.button("update selected files")
        if 'nodes' not in st.session_state.metainf or rfl:
            st.session_state.metainf['nodes'] = tree3._create_tree(
                "catalogue/"+cache_dir+"/data/")
            st.session_state.metainf['return_select'] = {'checked': [],
                                                         'expanded': []}
        with st.sidebar:
            # streamlit tree select docs: https://github.com/Schluca/streamlit_tree_select/tree/main
            st.write("**Please select here all files containing actual data:**")
            newchecks = copy.deepcopy(st.session_state.metainf['return_select'])
            newchecks = streamlit_tree_select.tree_select(
                st.session_state.metainf['nodes'],
#                only_leaf_checkboxes=True,
#                no_cascade=True,
                checked=newchecks['checked'],
                expanded=newchecks['expanded'])
            if ufl:
                st.session_state.metainf['return_select'] = copy.deepcopy(
                    newchecks)
                st.rerun()
#        with c1:
#            st.write(st.session_state.metainf['return_select'])


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

if 'nodes' in st.session_state.metainf and len(
        st.session_state.metainf['return_select']['checked']) > 0:
    if 'file_mapping' not in st.session_state.metainf:
        st.session_state.metainf['file_mapping'] = {}
    with c1:
        for file in st.session_state.metainf['return_select']['checked']:
            file = os.path.normpath(file).replace("\\", "/")
            if file not in st.session_state.metainf['file_mapping']:
                st.session_state.metainf['file_mapping'][file] = {}
            file_meta = st.session_state.metainf['file_mapping'][file]
            with st.expander(label="**"+str.split(
                    file, sep=cache_dir+"/data/")[-1]+"**"):
                if st.button(":red[Clear file metadata]", key="cf"+file):
                    file_meta = {}
                encodings = ["cp1252", "UTF-8", "ISO 8859-1"]
                if not os.path.isfile(file):
                    st.write("Something went wrong, is it a file?")
                else:
                    try:
                        file1 = open(os.path.normpath(file), 'r')
                        Lines = file1.readlines()
                        enco = file1.encoding
                        prevb = True
                    except:
                        enco = None
                        prevb = False
                        st.warning("Could not read your file by open().")
                    fmm1, fmm2, fmm3, fmm4 = st.columns(4)
                    with fmm1:
                        showprev = st.checkbox("File preview", key = "fp"+file)
                    with fmm2:
                        showsett = st.checkbox("File settings", key = "fs"+file)
                    with fmm3:
                        showcols = st.checkbox("Column settings", key = "cs"+file)
                    with fmm4:
                        showjson = st.checkbox("Show file metadata", key = "fm"+file)

                    if showjson:
                        st.json(file_meta)

                    if showprev:
                        if prevb:
                            st.header("File Preview")
                            ii=0
                            for line in Lines[0:st.number_input("Number of lines for preview",
                                                                key="pre"+file,
                                                                value=3)]:
                                ii+=1
                                st.text("*Line "+str(ii)+"*: "+line)
                        else:
                            st.write('File preview not possible.')

                    if showsett:
                        st.header("File settings")
                        fm1, fm2, fm3 = st.columns(3)
                        if 'encoding' not in file_meta:
                            file_meta['encoding'] = enco
                        with fm1:
                            file_meta['encoding'] = st.selectbox(
                                label="choose encoding",
                                key="enc"+file,
                                options=[file_meta['encoding']]+encodings)

                        if 'separator' not in file_meta:
                            file_meta['separator'] = ','
                        with fm2:
                            file_meta['separator'] = st.text_input(
                                "choose separator",
                                value=file_meta['separator'],
                                key="sep"+file)

                        if 'headerlines' not in file_meta:
                            file_meta['headerlines'] = 0
                        with fm3:
                            file_meta['headerlines'] = st.number_input(
                                "number of header lines",
                                key="header"+file,
                                value=file_meta['headerlines'])
                    try:
                        filedata = pd.read_csv(
                            os.path.normpath(file),
                            encoding=file_meta['encoding'],
                            sep=file_meta['separator'],
                            header=file_meta['headerlines'],
                            engine="python")
                        filedatab = True
                    except:
                        filedatab = False

                    if showsett and filedatab:
                        st.write("Your data looks to me like:")
                        filedata
                    if showsett and not filedatab:
                        st.write("Could not read file. Please change settings.")

                    if showcols and filedatab:
                        if st.button("(re-)get columns", key = "reg"+file) or\
                                'cols' not in file_meta:
                            file_meta['cols'] = {}
                            for col in filedata.columns:
                                if col not in file_meta['cols']:
                                    file_meta['cols'][col] = {}
                        st.header("Columns settings")
                        col = st.selectbox(
                            "Which Column",
                            options=[x for x in file_meta['cols']])
                        colmod = copy.deepcopy(file_meta['cols'][col])
                        action = st.radio("What to do on column "+col,
                                          options=["attribute column",
                                                   "split column",],
                                          horizontal=True,
                                          key="act"+file
                                          )

                        #colmod = file_meta['cols'][col]
                        if 'sep' not in colmod:
                            colmod['sep'] = None
                            for side in ['left', 'right']:
                                colmod[side] = {}
                                colmod[side]['col'] = None
                                colmod[side]['agrovoc'] = None
                                colmod[side]['unit'] = None
                            colmod['agrovoc'] = None
                            colmod['unit'] = None
                            colmod['data type'] = None #### @Jonas/Honza - put in here integer/str/date/coordinates...
                            colmod['numeric separator'] = None #### @Jonas/Honza - put in here integer/str/date/...
                            colmod['relations'] = None #### @Jonas/Honza - here we would need the relations to timestamps / IDs
                        if action == "split column":
                            colmod['sep'] = st.text_input("Split by",
                                                          value=colmod['sep'])
                            for side in ['left', 'right']:
                                colmod[side]['col'] = st.text_input(
                                    "New "+side+" column name",
                                    value=colmod[side]['col'])
                                colmod[side]['agrovoc'] = st.text_input(
                                    "Choose agrovoc concept",
                                    key="agro"+side,
                                    value=colmod[side]['agrovoc'])
                                colmod[side]['unit'] = st.text_input(
                                    "Select unit of measurement",
                                    key="unit"+side,
                                    value=colmod[side]['unit'])
                        if action == "attribute column":
                            colmod['agrovoc'] = st.text_input(
                                "Choose agrovoc concept",
                                colmod['agrovoc'],
                                key="agro"+file)
                            colmod['unit'] = st.text_input(
                                "Select unit of measurement",
                                value=colmod['unit'],
                                key="unit"+file)
                        if st.button("Update column", key="upd"+file):
                            file_meta['cols'][col] = copy.deepcopy(colmod)
                            del colmod

# do the column operartions
                        for x in file_meta['cols']:
                            if 'sep' in file_meta['cols'][x] and bool(file_meta['cols'][x]['sep']):
                                st.write("Splitting "+x+" by "+file_meta['cols'][x]['sep'])
                                filedata[[file_meta['cols'][x]['left']['col'],
                                          file_meta['cols'][x]['right']['col']]] = filedata[
                                              x].str.split(
                                                  file_meta['cols'][x]['sep'], expand=True)

                                filedata.loc[:, file_meta['cols'][x]['left']['col']] = pd.to_numeric(filedata.loc[:, file_meta['cols'][x]['left']['col']].str.replace("N ",""))
                                filedata.loc[:, file_meta['cols'][x]['right']['col']] = pd.to_numeric(filedata.loc[:, file_meta['cols'][x]['right']['col']])

                        filedata
                        st.write("Hooray now I can produce a map:")
                        st.map(filedata, latitude="Lat4326", longitude="Lon4326")
