# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""

from soilpulse.project_management import *
from soilpulse.resource_managers.filesystem import *
from soilpulse.resource_managers.mysql import *
from soilpulse.resource_managers.xml import *
from soilpulse.resource_managers.json import *
from soilpulse.data_publishers import *
from soilpulse.metadata_scheme import *
from soilpulse.db_access import EntityKeywordsDB, DBconnector

def establish_new_project(dbcon, user_id, **example):
    """
    use case function
    """
    print("\n\n" + 150 * "#")
    print("CREATE NEW PROJECT")
    print("\n".join([f"{k}: {v}" for k, v in example.items()]))
    print(150 * "#"+"\n")
    # example.update({"user_id": user_id})

    # create ResourceManager instance for new resource:
    try:
        project = ProjectManager(dbcon, user_id, **example)

    except DatabaseEntryError as e:
        # this exception is thrown when trying to add new ResourceManager with existing name into the database (for same user)
        # pass the error message to the user ... some pop-up window with the message
        print(e.message)
        pass
    except NotImplementedError:
        print(
            f"Publisher of requested DOI record related files 'is not supported.\nCurrently implemented publishers: {[', '.join([k for k in PublisherFactory.publishers.keys()])]}")

    else:
        # download files associated with the publisher record
        try:
            project.downloadPublishedFiles()
        except DOIdataRetrievalException as e:
            print(f"Files of DOI record couldn't be downloaded due to DOI data response error.\n{e.message}")

        # setting of files 'licensing' - this property should be available through GUI
        project.keepFiles = True

        # show the whole container tree
        project.showContainerTree()

        # new empty dataset is created and added to the ResourceManager
        newDataset = project.newDataset("Dataset test 1")
        # add some containers from the ResourceManager - will be done through the GUI
        newDataset.addContainers(project.getContainerByID([1, 2, 6]))

        # # show the dataset's container tree
        # newDataset.showContainerTree()
        # newDataset.getCrawled()

        project.updateDBrecord()

    return project

def load_existing_project(dbcon, user_id, project_id):
    """
    use case function
    """

    print("\n\n" + 150 * "#")
    print("LOAD EXISTING PROJECT")
    print(f"user_id: {user_id}\nproject_id: {project_id}")
    print(150 * "#"+"\n")

    # example = {"user_id": user_id, "id": project_id}
    example = {"id": project_id}
    # create ProjectManager instance for loaded resource:
    try:
        project = ProjectManager(dbcon, user_id, **example)

    except DatabaseEntryError as e:
        # this exception is thrown whne trying to add new ProjectManager with same name into the database (for same user)
        # pass the error message to the user ... some pop-up window with the message
        print(e.message)
        pass
    except NotImplementedError:
        print(
            f"Publisher of requested DOI record related files 'is not supported.\nCurrently implemented publishers: {[', '.join([k for k in PublisherFactory.publishers.keys()])]}")

    else:
        print(f"project files root: {project.temp_dir}")
        # show project details
        print(str(project))
        # show the whole container tree
        project.showContainerTree()

        #show paths of files and related containers
        project.showFilesStructure()
        # # change Resource name ... testing
        # project.name = "Jonas' dissertation"
        # project.updateDBrecord()

    return project


if __name__ == "__main__":
    # user identifier that will be later managed by some login framework in streamlit
    # it's needed for loading ProjectManagers from database - user can access only own resources
    user_id = 1
    # database connection to load/save projects and their structure
    dbcon = DBconnector.get_connector(project_files_root)
    # show current saved resources of user
    dbcon.printUserInfo(user_id)

    # example DOI records that can be used
    example_1 = {"name": "Jonas Lenz's dissertation package", "doi": "10.5281/zenodo.6654150"}
    example_2 = {"name": "", "doi": "10.5281/zenodo.6654150"}
    example_3 = {"name": "Michael Schmuker's neuromorphic_classifiers", "doi": "10.5281/zenodo.18726"}  # more lightweight repo
    example_4 = {"name": "Ries et al.", "doi": "10.6094/unifr/151460"}

    # do the use case
    # project1 = establish_new_project(dbcon, user_id, **example_1)
    # project1.keepFiles = False
    # load_id = project1.id
    # del project1
    # project2 = establish_new_project(dbcon, user_id, **example_3)


    load_existing_project(dbcon, user_id, 5)




    # print("all containers:\n{}".format('\n'.join([str(c) for c in ContainerHandlerFactory.containers.values()])))




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
