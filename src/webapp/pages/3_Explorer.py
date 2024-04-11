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

st.title("Here you can explore the datasets captured by SoilPulse.")

folder = ".\\catalogue"
datasets = [f.path for f in os.scandir(folder) if f.is_dir()]
datasetdict = {}

for x in datasets:
    with open(x+"/meta", 'rb') as handle:
        datasetdict[x.split("/")[-1].split("\\")[-1]] = pickle.load(handle)

#st.json(datasetdict)

columns = st.multiselect("Query for which colunns", options=["Lat4326","Lon4326"])
#columns = ["Lat4326","Lon4326"]
columns

def get_values(columns2):
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
                    file,
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

data = pd.concat(get_values(columns), ignore_index=True)
#categories = np.unique(data['dataset'])
#colors = np.linspace(0, 1, len(categories))
#colordict = dict(zip(categories, colors))
#data["Color"] = data['dataset'].apply(lambda x: colordict[x])

data.loc[:, "Color"] = "#0033FF"
data.loc[data.loc[:, "dataset"] == "105281zenodo6654150", "Color"] = "#FF0033"
data
st.map(data, latitude="Lat4326", longitude="Lon4326", color="Color")
