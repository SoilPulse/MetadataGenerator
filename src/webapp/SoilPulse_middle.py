# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 05:14:24 2024.

@author: JL
"""

import os
import streamlit as st

import pandas as pd
import numpy as np


def _add_dataset(new_doi, new_name):
    try:
        path = "./catalogue/"+new_doi+new_name
        os.makedirs(path)
        f = open(path+"/demofile2.txt", "x")
        f.write("Hi from SoilPulse!")
        f.close()
        st.write("Created Dataset.")
    except:
        st.warning("Dataset allready exists.")


def _get__local_datasets():
    return ["./catalogue/" + s for s in next(os.walk("./catalogue"))[1]]


def _create_tree(folder):
    sub_folder_dic = []
    for f in os.listdir(folder):
        f = os.path.join(folder, f)
        if os.path.isfile(f):
            sub_folder_dic.append(
                {
                    "label": f.split('\\')[-1].split('/')[-1],
                    "value": f
                    }
                )
        if os.path.isdir(f):
            sub_folder_dic.append(
                {
                    "label": f.split('\\')[-1].split('/')[-1],
                    "value": f,
                    "children": _create_tree(f)
                    }
                )
    return sub_folder_dic


def _show_container_content(container):
    st.write(container)
    pass


def _update_container(container):
    pass


def _reload_container(container):
    pass


def _getdatasetofcontainer(container):
    return "your fancy dataset"


def _visualize_data(container, mainID, agrovoc):
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    #chart_data is data got from container
    st.line_chart(chart_data)
    pass


def _update_local_db(dataset):
    pass


def _reload_local_db(dataset):
    pass
