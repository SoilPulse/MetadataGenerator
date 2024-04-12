# -*- coding: utf-8 -*-
"""
The Interface to the data explorer.

@author: JL
"""

import streamlit as st
import os
import numpy as np
import pickle
import pandas as pd
import json
import sys

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


# find values by key from dict/list https://stackoverflow.com/a/29652561
def _gen_dict_extract(key, var):
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in _gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in _gen_dict_extract(key, d):
                        yield result


def get_keys_of_dictlist(key, var):
    keys = _gen_dict_extract(key, var)
    keys = list(set([x for x in keys]))  # unique values
    keys = [i for i in keys if i is not None]  # avoid None
    return keys


def get_values(columns2, datasetdict):
    returndict = {}
    columns = columns2
    columns2.append("dataset")
    for z in datasetdict:
        for file in datasetdict[z]['file_mapping']:
            file_meta = datasetdict[z]['file_mapping'][file]
    #        st.json(file_meta)
            if columns[0] in json.dumps(file_meta):
    #            st.write("found "+column+" in "+file)
                filedata = pd.read_csv(
                    os.path.normpath(file),
                    encoding=file_meta['encoding'],
                    sep=file_meta['separator'],
                    header=file_meta['headerlines'],
                    engine="python")
                for x in file_meta['cols']:
                    if 'sep' in file_meta['cols'][x] and bool(file_meta['cols'][x]['sep']):
                        filedata[[file_meta['cols'][x]['left']['col'],
                                  file_meta['cols'][x]['right']['col']]] = filedata[
                                      x].str.split(
                                          file_meta['cols'][x]['sep'], expand=True)

                        filedata.loc[:, file_meta['cols'][x]['left']['col']] = pd.to_numeric(filedata.loc[:, file_meta['cols'][x]['left']['col']].str.replace("N ",""))
                        filedata.loc[:, file_meta['cols'][x]['right']['col']] = pd.to_numeric(filedata.loc[:, file_meta['cols'][x]['right']['col']])
                        filedata.loc[:, "dataset"] = z
        returndict[z] = filedata.loc[:,columns2]
    return returndict


############# start app
st.title("Here you can explore the datasets captured by SoilPulse.")

folder = "catalogue"
datasets = [f.path for f in os.scandir(folder) if f.is_dir()]
datasetdict = {}

for x in datasets:
    with open(x+"/meta", 'rb') as handle:
        xname = x.split("/")[-1].split("\\")[-1]
        meta = pickle.load(handle)
        if "file_mapping" in meta:
            datasetdict[xname] = meta

keys = get_keys_of_dictlist('agrovoc', datasetdict)  # get all agrovoc values
with st.expander('Show all keywords of queryable datasets:'):
    keys


with st.expander("All queryable datasets:"):
    for x in datasetdict:
        st.write("Looking at dataset **"+x+"** with those keys:")
        st.write(get_keys_of_dictlist('agrovoc', datasetdict[x]))
    #    st.json(datasetdict[x]['ZenodoFiles'])
        if not os.path.isdir("catalogue/"+x+"/data"):
            os.mkdir("catalogue/"+x+"/data")
        if len(os.listdir(os.path.normpath("catalogue/"+x+"/data/"))) > 0:
            st.success('data allready loaded')
        if st.button("(Re-)download relevant files", key="dw"+x):
            for z in datasetdict[x]['ZenodoFiles']:
                z['loaded'] = False
    #            st.json(z)
            st.write("downloading")
            res = rm.downloadPublishedFiles(
                datasetdict[x], os.path.normpath(
                        "catalogue/"+x+"/data/"))
            st.success("download complete.")

columns = st.multiselect("Query for which colunns", options=keys)
# columns = ["Lat4326","Lon4326"]

if st.button("query these columns"):
    data = pd.concat(get_values(columns, datasetdict), ignore_index=True)
    #categories = np.unique(data['dataset'])
    #colors = np.linspace(0, 1, len(categories))
    #colordict = dict(zip(categories, colors))
    #data["Color"] = data['dataset'].apply(lambda x: colordict[x])

    c1, c2 = st.columns(2)
    with c1:
        data
    with c2:
        data.loc[:, "Color"] = "#0033FF"
        data.loc[data.loc[:, "dataset"] == "105281zenodo6654150", "Color"] = "#FF0033"
        if ("Lat4326" in columns and "Lon4326" in columns):
            st.map(data, latitude="Lat4326", longitude="Lon4326", color="Color")
