# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""


from soilpulse.resource_management import ResourceManager
from soilpulse.metadatascheme import *


if __name__ == "__main__":
    resource = ResourceManager
    em = EntityManager

    print(EntityManager.metadataEntities)
    print("hello SoilPulse")