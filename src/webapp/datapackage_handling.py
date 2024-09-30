# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 08:46:16 2024

@author: jonas.lenz
"""
import inspect
if not 'Package' in dir():
    from frictionless import Package, steps, Pipeline, portals, Catalog
if not "os" in dir():
    import os
if not "json" in dir():
    import json
if not "st" in dir():
    import streamlit as st

if 'package' not in st.session_state:
    st.session_state.package = Package()
if 'pipe' not in st.session_state:
    st.session_state.pipe = ""
if 'counter' not in st.session_state:
    st.session_state.counter = 0

def main():
    st.title("frictionless data manipulation")

# expecting data package parsed from SoilPulse
# manipulate descriptor
    basepath = st.session_state.localproject.temp_dir
    pipe_path = basepath + "/pipe.txt"
    zenodo_path = basepath + "/zenodometa.json"
    descriptor_path = basepath + "/package.json"

    with st.sidebar:
        table = st.radio("Select resource table of this dataset package.", [x.name for x in st.session_state.package.resources])
        st.warning("add package top level view here?")

    if len(st.session_state.package.resources) <= 0:
        st.warning("There are no resources added by now, please select relevant resources from available files.")
        st.stop()
    else:
        with st.expander("original description"):
            st.json(st.session_state.package.to_descriptor())
        if st.button("save descriptor"):
            with open(descriptor_path, "w") as file:
                file.write(
                    str(st.session_state.package.to_descriptor())
                    )

    with st.expander("resource *"+table+"* before pipe"):
        st.write(st.session_state.package.get_resource(table).to_pandas())

    with st.expander("modify pipeline"):
        #st.write(dir(steps))
        steptype = st.selectbox("add transformation step", options = dir(steps))
        #st.write(steptype)
        dicci={}
        st.write(inspect.getfullargspec(eval("steps."+steptype)))
        for parme in inspect.getfullargspec(eval("steps."+steptype)).kwonlyargs:
            dicci[parme] = st.text_input(parme)
        st.write(dicci)
        st.warning("Add user friendly interface (EGU Demo adaptation) to create steps in here!")
        if st.toggle("(re)load existing pipe"):
            with open(pipe_path) as pipe:
                apipe = pipe.read()
        else:
            apipe = st.session_state.pipe
        apipe = st.text_area("modify pipeline", key = "modpipe"+str(st.session_state.counter), value = apipe)

    if not st.toggle("Run Pipeline steps"):
        st.stop()

    with st.expander("resource transformed"):
        if st.button("apply new Pipe", disabled = st.session_state.pipe == apipe):
            try:
                pipeline = Pipeline(steps= eval(apipe))
                st.write(pipeline)
                st.session_state.package.transform(pipeline)
                st.session_state.pipe = apipe
                st.session_state.counter += 1
                st.rerun()
            except Exception as e:
                st.warning("Invalid pipe:")
                st.warning(e)
                st.stop()
    #st.session_state.package.resources[0]
        fltable = st.session_state.package.get_resource(table).to_pandas()
        if "time" in fltable.index.names:
            fltable.index = fltable.index.set_levels( fltable.index.levels[1].astype("timedelta64[s]"), level = 1)
        fltable = fltable.reset_index()
        st.write(fltable.head())
    with st.expander("resource visualisation"):
        options = st.multiselect("choose relevant columns",
                             options = fltable.columns
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
                st.scatter_chart(fltable, y = sely, x = selx, color=selc)
            except Exception as e:
                st.warning("No chart possible.")
                st.warning(e)
        if st.toggle("table"):
            try:
                mylist = [selc, sely, selx]
                mylist = list(dict.fromkeys(mylist))
                st.write(fltable[mylist])
            except Exception as e:
                st.warning("No table possible.")
                st.warning(e)

    with st.expander("resource validation"):
        report = st.session_state.package.get_resource(table).validate()
        if st.button("show validate"):
            st.write(report)
            st.json(st.session_state.package.validate().to_json())

    st.warning("hard coded deposition ID")
    if not 'deposition_id' in st.session_state:
        st.session_state.deposition_id = 109575

    st.warning("missing option to enter APIkey")
    if report.valid:
        control = portals.ZenodoControl(
            metafn=zenodo_path,
            apikey=st.secrets["apikey"],
            base_url="https://sandbox.zenodo.org/api/",
            deposition_id = st.session_state.deposition_id
        )
        if st.button("upload"):
            try:
                st.session_state.deposition_id = st.session_state.package.publish(control=control)
                st.write(st.session_state.deposition_id)
            except Exception as e:
                st.warning(e)


### option to merge tables by foreign keys
#    table1 = "time"
#    table2 = "meta"
#    mylisttime = st.session_state.package.get_resource(table1).to_pandas()
#    mylistmeta = st.session_state.package.get_resource(table2).to_pandas()
#
#    mylistmerge = mylisttime.merge(mylistmeta, left_on = "No", right_on="No")
#
#    st.write(mylistmerge)
    #print(st.session_state.package.get_resource('bulk.density.g.cm-3_second.run').to_view())


    #print(st.session_state.package.get_resource('meta').to_view())
