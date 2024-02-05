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

import os
import pandas as pd
# import sys

# sys.path.insert(0, './src/soilpulse')
# import get_metadata as gm
# from soilpulse import get_metadata as gm


st.title("Here the content of a single file can be explored.")

# fill this list from file selection of Data Crawler
files = ["./catalogue/105281zenodo6654150/data/lenz2022/database/ready2.csv",
         "./catalogue/105281zenodo6654150/data/lenz2022/export/meta.csv"]
file = st.selectbox("Choose file", files)
encodings = ["ANSI", "UTF-8"] # fill list of possible encodings (Is there a generic Python function?)
# encodings might be also guesed by #import chardet -> chardet.detect(f), now it is done by file open

#if 'test' not in st.session_state:
#    st.session_state['test'] = False

if not os.path.isfile(file):
    st.write("Please go back to file download, the file can not be found!")
else:
    file1 = open(file, 'r')
    encodings = [file1.encoding]+encodings
    if st.checkbox("Show head of the raw file"):
        Lines = file1.readlines()
        st.write("The first three lines look like: ")
        for line in Lines[0:3]:
            st.write(line)
    with st.expander("file options",
#                     expanded=st.session_state['test'],
                     ):
        encoding_gues = st.radio("choose encoding", encodings, horizontal=True)
        separator = st.text_input("choose separator", value=",")
    try:
        filedata = pd.read_csv(file, encoding=encoding_gues, sep=separator)
    except:
        st.write("Encoding not correctly guesed, change file options.")
#        st.session_state['test'] = True

# filedata = pd.read_csv("../catalogue/105281zenodo6654150/data/lenz2022/database/ready2.csv", encoding="ANSI", sep=" ")

if 'filedata' in locals() or 'filedata' in globals():
    columnrecon = pd.DataFrame(columns=['SoilPulse Entity',
                                        'Given unit',
                                        'Factor to SI',
                                        'Na value',
                                        'Str.split',
                                        'split to 1',
                                        'split to 2',
                                        'links to'
                                        ],
#                               index = ["coordinates"]
                               index=filedata.columns
                               )

    columnrecon.loc["date", "SoilPulse Entity"] = "['Lon4326','Lat4326']"
    columnrecon.loc["coordinates", "Str.split"] = " \\| "
    columnrecon.loc["coordinates", "split to 1"] = "Lon4326"
    columnrecon.loc["coordinates", "split to 2"] = "Lat4326"

    columnrecon.loc["date", "SoilPulse Entity"] = "Date"
    columnrecon.loc["date", "Given unit"] = "YYYY-MM-DD"

    with st.expander("Table recipe"):
        columnrecon = st.data_editor(columnrecon,
                                     hide_index=False,
                                     )

    for col, meta in columnrecon.iterrows():
        if not pd.isna(meta["Str.split"]):
            try:
                st.write("Split column '"+col+"'")
                filedata[[meta["split to 1"], meta["split to 2"]]] = filedata[
                    col].str.split(meta["Str.split"], expand=True)
#                st.write("Split success!")
                filedata[meta["split to 1"]] = pd.to_numeric(
                    filedata[meta["split to 1"]])
                filedata[meta["split to 2"]] = pd.to_numeric(
                    filedata[meta["split to 2"]])
#                st.write("numeric convert!")
            except:
                st.write("Could not split.")

    if st.button("save recipe"):
        columnrecon.to_csv(file+".recipe")

    with st.expander("Table Data"):
        filedata

    if st.checkbox("Data visualisation"):
        if 'Lon4326' in filedata and 'Lat4326' in filedata:
            pointsdf = filedata[["Lat4326", "Lon4326"]]
            pointsdf["dataset"] = 2000
            if st.checkbox("add dataset 1"):
                df2 = pd.DataFrame([
                        [51.0796, 13.2912],
                        [51.0706, 13.2912],
                        [51.0746, 13.2912],
                        [51.0736, 13.2912]
                        ],
                    columns=['Lat4326',
                             'Lon4326'
                             ])
                df2["dataset"] = 2
                pointsdf = pd.concat([df2, pointsdf])
            if st.checkbox("add dataset 2"):
                df2 = pd.DataFrame([
                        [50.0006, 13.3912],
                        [50.0006, 13.2812],
                        [50.0860, 13.3912],
                        [50.0860, 13.2812]
                        ],
                    columns=['Lat4326',
                             'Lon4326'])
                df2["dataset"] = 30
                pointsdf = pd.concat([df2, pointsdf])
#            pointsdf["color"] = "#000000"
#            pointsdf["color"][pointsdf["dataset"]>1] = "#808080"
#            pointsdf
            st.map(pointsdf,
                   latitude="Lat4326",
                   longitude="Lon4326",
                   size="dataset",
#                   color="" # color does not work
                   )
        else:
            st.write("missing datapoints")

# recipe instructions from user dialog:
#   - file encoding and separator
#   - identification of relevant column
#   - further processing of column (strsplit), assignment entity type
#   -
