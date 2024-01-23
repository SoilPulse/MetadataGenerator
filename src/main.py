# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""


from soilpulse.resource_management import *
from soilpulse.metadatascheme import *


if __name__ == "__main__":
    exampleDOI = "10.5281/zenodo.6654150"

    ###### the resource initiation #####################
    # ResourceManager instance
    RM = ResourceManager("Jonas Lenz's dissertation files", exampleDOI)
    RM.showContents()

    # # this will be done by the UI
    # newDataset = DatasetHandlerFactory.createHandler("filesystem")
    # RM.datasets.append(newDataset)

    ###### dataset crawling and metadata structure mapping ################

    # something like this will happen
    # RM.dataset.MetadataStructureMap = newDataset.crawler.crawl()

    # but for now let's do it manually
    dataset = RM.datasets[0]
    EF = dataset.metadataMap.entityFactory
    title = dataset.metadataMap.addEntity(EF.createEntityInstance("title", "This is a first tile", "cs", "utf-8"), Pointer())
    title2 = dataset.metadataMap.addEntity(EF.createEntityInstance("title", "This is a second tile", "cs", "utf-8"), Pointer())

    dataset.checkMetadataStructure()

    # em.showEntityCount()
    # print("Minimum count check results:")
    # for entity in EF.checkMinCounts():
    #     if entity[2]<entity[1]:
    #         print("\tmissing element type '{}' (minimum count {}, current count {})".format(entity[0], entity[1], entity[2]))
    #
    # print("")
    #
    # print("Maximum count check results:")
    # for entity in EF.checkMaxCounts():
    #     if entity[2] > entity[1]:
    #         print("\ttoo many elements of type '{}' (maximum count {}, current count {})".format(entity[0], entity[1], entity[2]))

    # print("min counts: {}".format(em.checkMinCounts()))
    # print("max counts: {}".format(em.checkMaxCounts()))
    # em.showKeywordsMapping()


    print("\ndone.")