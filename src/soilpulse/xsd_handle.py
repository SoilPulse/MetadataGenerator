# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 00:53:23 2024

@author: JL
"""

import xmlschema
from pprint import pprint
schema = xmlschema.XMLSchema("https://web.bonares.de/md_schema/bonares/bonares.xsd")
#schema = xmlschema.XMLSchema("https://web.bonares.de/md_schema/apiso/apiso.xsd")
schema.export(target='my_schemas', save_remote=True)
schema = xmlschema.XMLSchema("my_schemas/apiso.xsd")  # works without internet
ab = xmlschema.XMLSchema.meta_schema.decode("my_schemas/apiso.xsd")

import lxml.etree as etree
x = etree.parse(r"C:\Users\JL\Downloads\10.4228zalf-qq16-t967\a282bf60-d7ca-4c36-875b-7b48ff6fcce1.xml")
print etree.tostring(x, pretty_print=True)