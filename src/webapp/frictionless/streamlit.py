# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 08:46:16 2024

@author: jonas.lenz
"""

from frictionless import Package, steps, Pipeline, portals, Catalog
import os
import json

if not "st" in dir():
    import streamlit as st

if 'pipe' not in st.session_state:
    st.session_state.pipe = ""
if 'counter' not in st.session_state:
    st.session_state.counter = 0

st.title("frictionless data manipulation")

#st.write(os.getcwd())


# expecting data package parsed from SoilPulse
# manipulate descriptor
with open("lenz2022_zip/datapackage.json") as file:
    des = file.read()

with st.expander("Initial datapackage definition"):
    st.json(des)
    st.warning("Modify by pipe")

try:
    st.session_state.package = Package("lenz2022_zip/datapackage.json")
except Exception as e:
    st.warning("could not load package")
    st.warning(e)
    st.stop()

with st.sidebar:
    table = st.radio("Select table", [x.name for x in st.session_state.package.resources])

with st.expander("resource before pipe"+table):
    #st.session_state.package.resources[0]
    st.write(st.session_state.package.get_resource(table).to_pandas())

with st.expander("modify pipeline"):
    if st.toggle("(re)load_pipe"):
        with open("./lenz2022_zip\\pipe.txt") as pipe:
            a = pipe.read()
    else:
        a = st.session_state.pipe
    a = st.text_area("modify pipeline", key = "modpipe"+str(st.session_state.counter), value = a)

if not st.toggle("Run Pipeline steps"):
    st.stop()

with st.expander("resource transformed"):
    if st.button("apply new Pipe", disabled = st.session_state.pipe == a):
        try:
            pipeline = Pipeline(steps= eval(a))
            st.write(pipeline)
            st.session_state.package.transform(pipeline)
            st.session_state.pipe = a
            st.session_state.counter += 1
            st.rerun()
        except Exception as e:
            st.warning("Invalid pipe:")
            st.warning(e)
            st.stop()
    #st.session_state.package.resources[0]
    a = st.session_state.package.get_resource(table).to_pandas()
    if "time" in a.index.names:
        a.index = a.index.set_levels( a.index.levels[1].astype("timedelta64[s]"), level = 1)
    a = a.reset_index()
    st.write(a.head())
with st.expander("resource visualisation"):
    options = st.multiselect("choose relevant columns",
                             options = a.columns
                             )
    colsel = st.columns(3)
    if len(options)>0:
        with colsel[0]:
            sely = st.selectbox("select column for y", options=options)
        with colsel[1]:
            selx = st.selectbox("select column for x", options=options)
        with colsel[2]:
            selc = st.selectbox("select column for color", options=options)


    if st.toggle("chart"):
        try:
            st.scatter_chart(a, y = sely, x = selx, color=selc)
        except Exception as e:
            st.warning("No chart possible.")
            st.warning(e)
    if st.toggle("table"):
        try:
            mylist = [selc, sely, selx]
            mylist = list(dict.fromkeys(mylist))
            st.write(a[mylist])
        except Exception as e:
            st.warning("No table possible.")
            st.warning(e)

with st.expander("resource validation"):
    report = st.session_state.package.get_resource(table).validate()
    if st.button("show validate"):
        st.write(report)
        st.json(st.session_state.package.validate().to_json())

if not 'deposition_id' in st.session_state:
    st.session_state.deposition_id = 109575

if report.valid:

    control = portals.ZenodoControl(
            metafn="zenodometa.json",
    #        apikey=st.secrets["apikey"],
            apikey="m2uSTiwu7ZBLu0IcpvK5MegmnDkfqCggpWe0skoFJNVvNgKtRzz0kM1HTxhy",
            base_url="https://sandbox.zenodo.org/api/",
            deposition_id = st.session_state.deposition_id
        )
    if st.button("upload"):
        try:
            st.session_state.deposition_id = st.session_state.package.publish(control=control)
            st.write(st.session_state.deposition_id)
        except Exception as e:
            st.warning(e)



table1 = "time"
table2 = "meta"
mylisttime = st.session_state.package.get_resource(table1).to_pandas()
mylistmeta = st.session_state.package.get_resource(table2).to_pandas()

mylistmerge = mylisttime.merge(mylistmeta, left_on = "No", right_on="No")

st.write(mylistmerge)
#print(st.session_state.package.get_resource('bulk.density.g.cm-3_second.run').to_view())


#print(st.session_state.package.get_resource('meta').to_view())

