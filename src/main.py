# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""


from soilpulse.resource_management import ResourceManager
from soilpulse.metadatascheme import *


if __name__ == "__main__":
    resource = ResourceManager
    em = EntityManager

    print(em.metadataEntities)

    try:
        title = em.createEntityInstance("title", "This is a first tile")
        # title2 = em.createEntityInstance("title", "This is a second tile")
    except MetadataSchemeException:
        print("Too many entities")

    print(title)

    print(em.currentCount)
    print("done.")