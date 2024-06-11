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
from soilpulse.db_access import EntityKeywordsDB, DBconnector

# user identifier that will be later managed by some login framework in streamlit
# it's needed for loading ResourceManagers from database - user can access only own resources
user_id = 1

# example DOI records that can be used
example_1 = {"name": "Jonas Lenz's dissertation package", "doi": "10.5281/zenodo.6654150"}
example_2 = {"name": "Michael Schmuker's neuromorphic_classifiers", "doi": "10.5281/zenodo.18726"}  # more lightweight repo
example_3 = {"name": "Ries et al.", "doi": "10.6094/unifr/151460"}
example_4 = {"name": None, "doi": None, "id": 9}


if __name__ == "__main__":
    # database connection to load/save
    dbcon = DBconnector()

    print("\n"+50*"=")
    userinfo = dbcon.getUserNameByID(user_id)
    usersResources = dbcon.getResourcesOfUser(user_id=user_id)
    if usersResources is not None:
        print(f"Saved ResourceManagers of user id = {user_id} ({userinfo[1]}, {userinfo[0]})")
        for rid, rname in usersResources.items():
            print(f"\t{rid}: {rname}")
    else:
        print(f"User id = {user_id} ({userinfo[1]}, {userinfo[0]}) has no saved Resource project.")
    print(50*"="+"\n")

    print("\n"+40*"|/|\\"+"\n\n")


    ###### the resource initiation #####################
    # get mockup example dictionary
    example = example_1
    example.update({"user_id": user_id})

    # create ResourceManager instance for new/loaded resource:
    try:
        RM = ResourceManager(**example)

    except DatabaseEntryError as e:
        # pass the error message to the user ... some pop-up window with the message
        print(e.message)
        pass
    else:

        # on initiation (or change of DOI) the RM:
            # loads information about files that are part of the DOI provided
            # unpacks archives
            # goes through the files, recognizes their type
            # creates ContainerHandler instances for all of them
                # ContainerHandlers execute inner structure recognition and fill their properties acoording to type
            # create the content tree of the ResourceManager - this tree should be returned to the frontend to display it to the user

            # loads metadata information that are part of data obtained from DOI record or data host record

        print(f"Current ResourceManager's ID is {RM.id}")
        # download files associated with the publisher record
        RM.downloadPublishedFiles()
        # # show the whole container tree
        # RM.showContainerTree()


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