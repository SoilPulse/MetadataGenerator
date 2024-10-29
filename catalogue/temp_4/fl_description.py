# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 13:53:33 2024

@author: JL
"""

from frictionless import Resource, Package, Pipeline, steps, transform
import os
import json
from pathlib import Path
from frictionless import steps, transform, Detector

# load prepared package with defined comment rows of the three tables, but no schema
ries = Package("catalogue\\temp_4\\example_Ries.json")

# infer schema
ries.infer()

# parse metadata in files to frictionless
for x in ries.resources:
    # open files from unzipped files
    with open("catalogue\\temp_4\\"+x.path.replace(".zip","")+"/"+x.innerpath) as f:
        for z in f.readlines():
            # comment rows starting with "# - " hold metadata on data columns
            # units are in "[]"
            if "#	- " in z:
#                print(z)
                z = z.replace("#	- ", "")
                abb = z.split(":")
#                print(abb)
                for field in x.schema.fields:
                    if abb[0] == field.name:
                        try:
                            desc = abb[1].split("[")
                            x = transform(x,
                                          steps = [
                                              steps.field_update(name = field.name,
                                                                 descriptor = {
                                                                     'description': desc[0],
                                                                     'unit': desc[1].replace(" ","").replace("]\n","")
                                                                     }
                                                                 )
                                              ]
                                          )
                        except:
                            print("failed on resource: "+x.name+"\nfield: "+field.name)
    x.schema.missing_values += ['NA']

# type adjustments, as falsely infered by fl
x = ries.resources[2]
numeric_list = [x.name for x in ries.resources[2].schema.fields if "Q_" in x.name or "P_" in x.name]
print(numeric_list)
for z in numeric_list:
    x = transform(x,
                  steps = [
                      steps.field_update(name = z,
                                         descriptor = {
                                             'type': "number"
                                             }
                                         )
                      ]
                  )
x = transform(x,
             steps = [
                 steps.field_update(name = "Date_time",
                                    descriptor = {
                                        'type': "datetime",
                                        'format': "%Y-%m-%d %H:%M" # time zone offset is missing
#                                        'format': "%Y-%m-%d %H:%M %z+0200"
                                        }
                                    )
                 ]
             )

# set primary and foreign keys
ries.resources[0].schema.primary_key = ["Site_number"]
ries.resources[1].schema.primary_key = ["Site_number", "Experiment_number"]
ries.resources[1].schema.foreign_keys = [
    {'fields': ['Site_number'],
     'reference': {
         "resource": ries.resources[0].name,
         "fields": [
            "Site_number"
            ]
         }
     }
     ]
ries.resources[2].schema.primary_key = ["Site_number", "Date_time"]
ries.resources[2].schema.foreign_keys = [
    {'fields': ['Site_number'],
     'reference': {
         "resource": ries.resources[0].name,
         "fields": [
            "Site_number"
            ]
         }
     }#, # the following foreign key is correct in principal, but is invalid, as not all timesteps belong to an experiment
#     {'fields': ['Site_number', 'Experiment_number'],
#      'reference': {
#          "resource": ries.resources[1].name,
#          "fields": [
#             "Site_number",
#             'Experiment_number'
#             ]
#          }
#      }
     ]


ries.to_json("catalogue\\temp_4\\primary_package.json")