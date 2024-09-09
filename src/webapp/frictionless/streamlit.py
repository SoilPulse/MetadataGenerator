# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 08:46:16 2024

@author: jonas.lenz
"""

from frictionless import Package, steps, Pipeline
import os

import streamlit as st

st.title("frictionless data manipulation")

st.write(os.getcwd())

with open("lenz2022_zip/datapackage (1).json") as file:
    des = file.read()

with st.expander("datapackage definition"):
    des = st.text_area("mod", value = des)

try:
    res2 = Package("lenz2022_zip/datapackage (1).json")
except Exception as e:
    st.warning("could not load package")
    st.warning(e)

with st.sidebar:
    table = st.radio("Select table", [x.name for x in res2.resources])

with st.expander("resource "+table):
    #res2.resources[0]
    st.write(res2.get_resource(table).to_pandas())

with open("./lenz2022_zip\\pipe.txt") as pipe:
    a = pipe.read()

try:
    pipeline = Pipeline(steps= eval(a))
    st.write(pipeline)
    res2.transform(pipeline)
except Exception as e:
    st.warning("No pipe possible.")
    st.warning(e)

with st.expander("resource transformed"):
    #res2.resources[0]
    a = res2.get_resource(table).to_pandas()
#    st.write(a)
    options = st.multiselect("choose relevcant columns", options = a.columns)
    if len(options)>0:
        colsel = st.columns(3)

        with colsel[0]:
            sely = st.selectbox("select column for y", options=options, index = 1)
        with colsel[1]:
            selx = st.selectbox("select column for x", options=options, index = 2)
        with colsel[2]:
            selc = st.selectbox("select column for color", options=options, index = 0)

    if st.toggle("chart or data"):
        try:
            st.scatter_chart(a, y = sely, x = selx, color=selc)
        except Exception as e:
            st.warning("No chart possible.")
            st.warning(e)
    else:
        try:
            mylist = [selc, sely, selx]
            mylist = list(dict.fromkeys(mylist))
            st.write(a[mylist])
        except Exception as e:
            st.warning("No table possible.")
            st.warning(e)

with st.expander("resource validation"):
    st.json(res2.validate().to_json())


#print(res2.get_resource('bulk.density.g.cm-3_second.run').to_view())


#print(res2.get_resource('meta').to_view())

