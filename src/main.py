# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""

from soilpulse.resource_management import *
from soilpulse.resource_managers.filesystem import *
from soilpulse.resource_managers.mysql import *
from soilpulse.resource_managers.xml import *
from soilpulse.resource_managers.json import *
from soilpulse.data_publishers import *
from soilpulse.metadata_scheme import *
from soilpulse.db_access import EntityKeywordsDB


if __name__ == "__main__":
    print("\n"+40*"|/|\\"+"\n\n")
    # example DOI records that can be published
    example_1 = {"name": "Jonas Lenz's dissertation package", "doi": "10.5281/zenodo.6654150"}
    example_2 = {"name": "Michael Schmuker's neuromorphic_classifiers", "doi": "10.5281/zenodo.18726"} # more lightweight repo
    example_3 = {"name": "Ries et al.", "doi": "10.6094/unifr/151460"}

    ###### the resource initiation #####################
    # create ResourceManager instance for newly established resource:
    RM = ResourceManager(**example_1)
    # on initiation (or change of DOI) the RM:
        # loads information about files that are part of the DOI provided
        # unpacks archives
        # goes through the files, recognizes their type
        # creates ContainerHandler instances for all of them
            # ContainerHandlers execute inner structure recognition and fill their properties acoording to type
        # create the content tree of the ResourceManager - this tree should be returned to the frontend to display it to the user

        # loads metadata information that are part of data obtained from DOI record or data host record

    print(f"Newly established resource's ID is {RM.id}")
    # download files associated with the publisher record
    RM.downloadPublishedFiles()
    # # show the whole container tree
    # RM.showContainerTree()



    # create ResourceManager instance for resource already existing in DB - loading resource:
    # RM = ResourceManager(id=1)

    # new empty dataset is created and added to the ResourceManager
    newDataset = RM.newDataset("Dataset test 1")
    # add some containers from the ResourceManager - will be done through the GUI
    newDataset.addContainers(RM.getContainerByID([1, 2, 6]))

    # show the dataset's container tree
    newDataset.showContainerTree()
    newDataset.getCrawled()


    ###### dataset metadata structure mapping ################

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