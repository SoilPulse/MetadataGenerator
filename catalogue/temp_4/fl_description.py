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
numeric_list = [x.name for x in ries.resources[2].schema.fields if "Q_" in x.name or "P_" in x.name]
print(numeric_list)
x = ries.resources[2]
x = transform(x,
             steps = [
                     steps.field_update(name = z,
                                        descriptor = {
                                        'type': "number"
                                        }
                                    )
                     for z in numeric_list
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

numeric_list = [x.name for x in ries.resources[1].schema.fields if "Q_" in x.name or "P_" in x.name or "RC_" in x.name]
print(numeric_list)
x = ries.resources[1]
x = transform(x,
             steps = [
                 steps.field_update(name = z,
                                    descriptor = {
                                        'type': "number"
                                        }
                                    )
                     for z in numeric_list
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


# manual assignment of concepts by Agrovoc URI
#field_list = []
#for y in ries.resources:
#    field_list += [x.name for x in y.schema.fields ]
concepts = {'Site_number': '',
 'Site_name': 'http://aims.fao.org/aos/agrovoc/c_330988',
 'Coordinates': 'http://aims.fao.org/aos/agrovoc/c_64a2abf9',
 'Elevation': 'http://aims.fao.org/aos/agrovoc/c_316',
 'Slope': 'http://aims.fao.org/aos/agrovoc/c_fa256eab',
 'Slope_aspect': 'http://aims.fao.org/aos/agrovoc/c_1832474d',
 'Land_use': 'http://aims.fao.org/aos/agrovoc/c_4182',
 'Vegetation': 'https://agrovoc.fao.org/browse/agrovoc/en/page/c_8176',
 'Vegetation_height': 'https://agrovoc.fao.org/browse/agrovoc/en/page/c_61f3cae5',
 'Plant_coverage': '',
 'Geology_GUEK300': '',
 'Sand_10cm': '',
 'Silt_10cm': '',
 'Clay_10cm': 'http://aims.fao.org/aos/agrovoc/c_15619',
 'Sand_30cm': '',
 'Silt_30cm': '',
 'Clay_30cm': 'http://aims.fao.org/aos/agrovoc/c_15619',
 'Sand_50cm': '',
 'Silt_50cm': '',
 'Clay_50cm': 'http://aims.fao.org/aos/agrovoc/c_15619',
 'Bulk_density_10cm': 'http://aims.fao.org/aos/agrovoc/c_7167',
 'Bulk_density_30cm': 'http://aims.fao.org/aos/agrovoc/c_7167',
 'Bulk_density_50cm': 'http://aims.fao.org/aos/agrovoc/c_7167',
 'Stone_content_10cm': '',
 'Stone_content_30cm': '',
 'MP_density_2mm_10cm': 'http://aims.fao.org/aos/agrovoc/c_35318',
 'MP_density_2mm_30cm': 'http://aims.fao.org/aos/agrovoc/c_35318',
 'MP_density_5mm_10cm': 'http://aims.fao.org/aos/agrovoc/c_35318',
 'MP_density_5mm_30cm': 'http://aims.fao.org/aos/agrovoc/c_35318',
 'SOM_10cm': 'http://aims.fao.org/aos/agrovoc/c_389fe908',
 'SOM_30cm': 'http://aims.fao.org/aos/agrovoc/c_389fe908',
 'SOM_50cm': 'http://aims.fao.org/aos/agrovoc/c_389fe908',
 'Total_porosity_10cm': 'http://aims.fao.org/aos/agrovoc/c_7184',
 'Total_porosity_30cm': 'http://aims.fao.org/aos/agrovoc/c_7184',
 'Total_porosity_50cm': 'http://aims.fao.org/aos/agrovoc/c_7184',
 'Site_number': '',
 'Experiment_number': '',
 'Experiment_start': '',
 'Experiment_end': '',
 'Experiment_duration': '',
 'Return_period': '',
 'Target_intensity': '',
 'Data_quality_comment': '',
 'Selected_subplots': '',
 'P_RG_1': '',
 'P_RG_2': '',
 'P_RG_3': '',
 'P_RG_4': '',
 'P_RG_5': '',
 'P_RG_6': '',
 'P_C_1': '',
 'P_C_2': '',
 'P_C_3': '',
 'P_C_4': '',
 'P_C_5': '',
 'P_C_6': '',
 'P_C_7': '',
 'P_C_8': '',
 'P_C_9': '',
 'P_C_10': '',
 'P_C_11': '',
 'P_subplot_A': '',
 'P_subplot_B': '',
 'P_subplot_C': '',
 'P_mean_selected': '',
 'Q_OF_subplot_A': 'http://aims.fao.org/aos/agrovoc/c_c9214ebe',
 'Q_OF_subplot_B': 'http://aims.fao.org/aos/agrovoc/c_c9214ebe',
 'Q_OF_subplot_C': 'http://aims.fao.org/aos/agrovoc/c_c9214ebe',
 'Q_SSF_subplot_B': 'http://aims.fao.org/aos/agrovoc/c_35389',
 'Q_OF_mean_selected': 'http://aims.fao.org/aos/agrovoc/c_c9214ebe',
 'RC_OF_subplot_A': 'own:runoff_coefficient',
 'RC_OF_subplot_B': 'own:runoff_coefficient',
 'RC_OF_subplot_C': 'own:runoff_coefficient',
 'RC_SSF_subplot_B': 'own:runoff_coefficient',
 'RC_OF_mean_selected': 'own:runoff_coefficient',
 'Date_time': '',
 'Site_number': '',
 'Experiment_number': '',
 'Land_use': '',
 'Selected_subplots': '',
 'Experiment_duration': '',
 'Return_period': '',
 'Experiment_time_step_min': '',
 'Experiment_time_step_plus10min': '',
 'Solar_radiation': '',
 'Wind_direction': '',
 'Wind_speed': '',
 'Air_temperature': 'http://aims.fao.org/aos/agrovoc/c_230',
 'Relative_humidity': '',
 'P_RG_1': '',
 'P_RG_2': '',
 'P_RG_3': '',
 'P_RG_4': '',
 'P_RG_5': '',
 'P_RG_6': '',
 'P_subplot_A': '',
 'P_subplot_B': '',
 'P_subplot_C': '',
 'P_mean_selected': '',
 'SM1_5cm': '',
 'SM1_10cm': '',
 'SM1_20cm': '',
 'SM1_30cm': '',
 'SM1_40cm': '',
 'SM2_5cm': '',
 'SM2_10cm': '',
 'SM2_20cm': '',
 'SM2_30cm': '',
 'SM2_40cm': '',
 'WT1_height': '',
 'WT2_height': '',
 'Q_OF_subplot_A': '',
 'Q_OF_subplot_B': '',
 'Q_OF_subplot_C': '',
 'Q_SSF_subplot_B': '',
 'Q_OF_mean_selected': ''}

# parse concepts to frictionless
for x in ries.resources:
    x = transform(x,
              steps = [
                      steps.field_update(name = field.name,
                                         descriptor = {
                                             'concept': concepts[field.name]
                                             }
                                         )
                       for field in x.schema.fields
                      ]
                  )

ries.validate()



ries.to_json("catalogue\\temp_4\\primary_package.json")

# do data transformation

with open('catalogue\\temp_4\\to_publish\\pipe.txt', 'r') as f:
    pipe = Pipeline(steps=eval(f.read()))

ries.transform(pipe)
ries.validate()
ries.to_json("catalogue\\temp_4\\to_publish\\piped_package.json")
