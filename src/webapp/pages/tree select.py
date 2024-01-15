# -*- coding: utf-8 -*-

import streamlit as st
from streamlit_tree_select import tree_select
import os
from typing import Dict, List

#### this is the structure we will need
# # Create nodes to display
# nodes = [
#     {"label": "Folder A", "value": "folder_a"},
#     {
#         "label": "Folder B",
#         "value": "folder_b",
#         "children": [
#             {"label": "Sub-folder A", "value": "sub_a"},
#             {"label": "Sub-folder B", "value": "sub_b"},
#             {"label": "Sub-folder C", "value": "sub_c"},
#         ],
#     },
#     {
#         "label": "Folder C",
#         "value": "folder_c",
#         "children": [
#             {"label": "Sub-folder D", "value": "sub_d"},
#             {
#                 "label": "Sub-folder E",
#                 "value": "sub_e",
#                 "children": [
#                     {"label": "Sub-sub-folder A", "value": "sub_sub_a"},
#                     {"label": "Sub-sub-folder B", "value": "sub_sub_b"},
#                 ],
#             },
#             {"label": "Sub-folder F", "value": "sub_f"},
#         ],
#     },
# ]


def create_tree(sub_folder_dict):
    tree = []
    iteratordic = iter(sub_folder_dict.items())
    k, v = next(iteratordic)
    tree.append(create_node(k, v, sub_folder_dict))
    return tree


def create_node( abs_path: str, sub_folders: List[str], sub_folder_dict: Dict[str, List[str]]):
    node = {"label": abs_path.split('\\')[-1], "value": abs_path}
    if sub_folders:
        node["children"] = []
        for sub_folder in sub_folders:
            abs_path = os.path.join(abs_path, sub_folder)
#            if os.path.isdir(abs_path):
            node["children"].append(create_node(abs_path, sub_folder_dict.get(abs_path, []), sub_folder_dict))
    return node


def get_child_folder_dic(par_folder_path, recursive=False) -> Dict[str, List[str]]:
    sub_folder_dic = {}
    for root, dirs, files in os.walk(os.path.join(par_folder_path)):
        sub_folder_dic[root] = dirs+files
    return sub_folder_dic
        
nodes = create_tree(get_child_folder_dic(par_folder_path='.\\catalogue\\105281zenodo6654150\\data\lenz2022', recursive = True))

with st.sidebar:
    return_select = tree_select(nodes)

st.header("selected nodes")
st.write(return_select)
st.header("node list")
st.write(nodes)