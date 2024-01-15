# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""


from soilpulse.resource_management import ResourceManager
from soilpulse.metadatascheme import *


if __name__ == "__main__":
    resource = ResourceManager
    entityFactory = EntityManager

    title = entityFactory.createEntityInstance("title", "This is a first tile", "cs", "utf-8")
    title2 = entityFactory.createEntityInstance("title", "This is a second tile", "cs", "utf-8")

    # em.showEntityCount()
    print("Minimum count check results:")
    for entity in entityFactory.checkMinCounts():
        if entity[2]<entity[1]:
            print("\tmissing element type '{}' (minimum count {}, current count {})".format(entity[0], entity[1], entity[2]))

    print("")

    print("Maximum count check results:")
    for entity in entityFactory.checkMaxCounts():
        if entity[2] > entity[1]:
            print("\ttoo many elements of type '{}' (maximum count {}, current count {})".format(entity[0], entity[1], entity[2]))

    # print("min counts: {}".format(em.checkMinCounts()))
    # print("max counts: {}".format(em.checkMaxCounts()))
    # em.showKeywordsMapping()


    print("\ndone.")