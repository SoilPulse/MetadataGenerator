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


#detector = Detector(field_missing_values=["", "NA"])
#ries = Package("catalogue\\temp_4\\example_Ries.json", detector = detector)
ries = Package("catalogue\\temp_4\\example_Ries.json")

ries.infer()

for x in ries.resources:
#if True:
#    x = ries.resources[1]
    with open("catalogue\\temp_4\\"+x.path.replace(".zip","")+"/"+x.innerpath) as f:
        for z in f.readlines():
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
ries.resources[2].validate()

ries.to_json("catalogue\\temp_4\\primary_package.json")