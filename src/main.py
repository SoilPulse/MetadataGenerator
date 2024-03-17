# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""

from soilpulse.resource_management import *
from soilpulse.resource_managers.filesystem import *
from soilpulse.resource_managers.mysql import *
from soilpulse.resource_managers.xml import *
from soilpulse.metadata_scheme import *
from soilpulse.db_access import EntityKeywordsDB


if __name__ == "__main__":
    print(EntityKeywordsDB.DBs)



    exampleDOI = "10.5281/zenodo.6654150"

    ###### the resource initiation #####################
    # ResourceManager instance
    RM = ResourceManager("Jonas Lenz's dissertation files", exampleDOI)
    # on initiation (or change of DOI) the RM:
        # loads files that are part of the DOI provided
        # unpacks archives
        # goes through the files, recognizes their type
        # creates ContainerHandler instances for all of them
            # ContainerHandlers execute inner structure recognition and fill their properties acoording to type
        # create the content tree of the ResourceManager - this tree should be returned to the frontend to display it to the user

        # loads metadata information that are part of data obtained from DOI record or data host record


    newDataset = Dataset("Dataset 1")
    RM.addDataset(newDataset)
    # RM.setDOI("10.5281/zenodo.665415")

    RM.showContainerTree()



    ###### dataset crawling and metadata structure mapping ################

    # something like this will happen
    # RM.dataset.MetadataStructureMap = newDataset.crawler.crawl()

    # but for now let's do it manually
    # dataset = RM.datasets[0]
    # EF = dataset.metadataMap.entityFactory
    # title = dataset.metadataMap.addEntity(EF.createEntityInstance("title", "This is a first tile", "en", "utf-8"), Pointer())
    # title2 = dataset.metadataMap.addEntity(EF.createEntityInstance("title", "This is a second tile", "en", "utf-8"), Pointer())

    # dataset.checkMetadataStructure()

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
    # print("max counts: {}".format(em.checkMaxCounts()))EF.showSearchExpressions()

    # EF.showSearchExpressions()


    print("\ndone.")