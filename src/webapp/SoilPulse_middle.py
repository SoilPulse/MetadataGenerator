# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 05:14:24 2024.

@author: JL
"""

import os


def _get__local_datasets():
    return []


def _add_dataset(new_doi, new_name):
    pass


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
