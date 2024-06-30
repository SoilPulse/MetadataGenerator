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


def _get_conceptsofsubcontainers(container):
    # queries actual and all subcontainers for controlled vocabularies
    return ["Soil organic carbon", "Sand"]


def _get_data_for_concept(container, agrovoc):
    # queries actual and all subcontainers for data of controlled vocabularies and their main identifier
    if container == 1:
        data = pd.DataFrame([[2],
                             [1.5],
                             [2.3],
                             [-0.5],
                             [1]],
                            columns=[container])
    else:
        data = pd.DataFrame(np.random.randn(5, 1),
                            columns=[str(container)])
    return data


def _get_datasets_by_concept(agrovoc):
    return [2, 3, 4]


def _visualize_data(container, mainID, agrovoc, datasets=[]):
    chart_data = _get_data_for_concept(1, "Runoff")
    for x in datasets:
        chart_data[str(x)] = _get_data_for_concept(x, "Runoff")[str(x)]
    # chart_data is data got from container
    st.write(chart_data)
    st.write("showing mockup data")
    st.line_chart(chart_data)
    pass


def _update_local_db(dataset):
    pass


def _reload_local_db(dataset):
    pass
