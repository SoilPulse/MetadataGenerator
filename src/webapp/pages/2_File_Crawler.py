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

# fill this list from file selection of Data Crwaler
files = ["./catalogue/105281zenodo6654150/data/lenz2022/database/ready2.csv"]
encodings = ["ANSI", "UTF-8"]
# encodings might be guesed by #import chardet -> chardet.detect(f)

for file in files:
    if not os.path.isfile(file):
        st.write("Please go back to file download!")
    else:
        st.write("Looking at file: "+file)
        st.write("The first three lines look like: ")
        file1 = open(file, 'r')
        Lines = file1.readlines()
        encodings = [file1.encoding]+encodings
        for line in Lines[0:3]:
            st.write(line)
        encoding_gues = st.radio("choose encoding", encodings, horizontal=True)
        separator = st.text_input("choose separator", value=",")
        try:
            filedata = pd.read_csv(file, encoding=encoding_gues, sep=separator)
            filedata
            filedata[['Lon4326', 'Lat4326']] = filedata['coordinates'].str.split(
                ' \\| ', expand=True)
            filedata['Lon4326'] = pd.to_numeric(filedata['Lon4326'])
            filedata['Lat4326'] = pd.to_numeric(filedata['Lat4326'])
            st.map(filedata, latitude="Lat4326", longitude="Lon4326")

        except:
            st.write("Encoding not correctly guesed.")


# recipe instructions from user dialog:
#   - file encoding and separator
#   - identification of relevant column
#   - further processing of column (strsplit), assignment entity type
#   -
