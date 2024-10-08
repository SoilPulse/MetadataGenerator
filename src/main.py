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
from soilpulse.db_access import EntityKeywordsDB, DBconnector, MySQLConnector, NullConnector


from pathlib import Path

soilpulse_root_dir_name = "SoilPulse"
project_files_dir_name = "project_files"
project_files_root = Path(Path.home(), soilpulse_root_dir_name, project_files_dir_name)

project_files_root.mkdir(parents=True, exist_ok=True)

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
    except DOIdataRetrievalException as e:
        print("Problems occurred while trying to retrieve DOI data:")
        print(e.message)
    else:
        # download files associated with the publisher record
        try:
            project.downloadPublishedFiles()
        except DOIdataRetrievalException as e:
            print(f"Files of DOI record couldn't be downloaded due to DOI data response error.\n{e.message}")
        else:
            # setting of files 'licensing' - this property should be available through GUI
            project.keepFiles = True
            # show the whole container tree
            project.showContainerTree()


            project.updateDBrecord()

        return project
    return


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
        if project.initialized:
            # print(f"project files root: {project.temp_dir}")
            # show project details
            print(str(project))

            #show paths of files and related containers
            # project.showFilesStructure()
            # change Resource name ... testing
            project.name = "Jonas' dissertation"

            # show the whole container tree
            project.showContainerTree()

            # CREATE AND WORK WITH DATASET
            # new empty dataset is created and added to the ResourceManager
            newDataset = project.newDataset("TUBAF Rainfall simulations")
            # add some containers from the ResourceManager - will be done through the GUI
            newDataset.addContainers(project.getContainerByID([771, 956, 992]))

            # upload vocabulary of concepts
            project.updateConceptsVocabularyFromFile(r"c://Users//jande//SoilPulse//project_files//_concepts2.json")
            print(f"loaded concept vocabulary: {project.conceptsVocabulary}")

            # do whatever the automated crawling is capable of
            newDataset.getCrawled()

            # and do some manual tweaking
            # like removing all concepts from container
            project.getContainerByID(776).removeAllConcepts()
            project.getContainerByID(778).removeAllConcepts()

            # assigning a concept to container
            project.getContainerByID(776).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})
                # this one is wrong and shoouldn't be there ...
            project.getContainerByID(778).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})
            project.getContainerByID(778).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_36811"})
            project.getContainerByID(778).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_36811"})
            project.getContainerByID(778).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_4260"})
            project.getContainerByID(778).addConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_4260"})


            # removing a concept from container
                # ... so it's removed
            project.getContainerByID(778).removeConcept({"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})

            # update vocabulary by concepts collected from containers
            project.updateConceptsVocabularyFromContents()

            # show the dataset's content
            newDataset.showContents(show_containers=True)

            # update database record

            project.updateDBrecord()

    return

def load_project_upload_files(dbcon, user_id, project_id):
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
        if project.initialized:
            # print(f"project files root: {project.temp_dir}")
            # show project details
            print(str(project))

            project.uploadFilesFromSession(["d:\\downloads\\test_file_3.txt", "d:\\downloads\\test_file_4.csv"])
            project.uploadFilesFromSession("d:\\downloads\\test_files.rar")

            # show the whole container tree
            project.showContainerTree()

            # show paths of files and related containers
            project.showFilesStructure()

            # update database record
            # project.updateDBrecord()

    return

if __name__ == "__main__":
    # user identifier that will be later managed by some login framework in streamlit
    # it's needed for loading ProjectManagers from database - user can access only own projects
    user_id = 1
    # example DOI records that can be used
    example_1 = {"name": "Jonas Lenz's dissertation package", "doi": "10.5281/zenodo.6654150"}
    example_2 = {"name": "", "doi": "10.5281/zenodo.6654150"}
    example_3 = {"name": "Michael Schmuker's neuromorphic_classifiers", "doi": "10.5281/zenodo.18726"}  # more lightweight repo
    example_4 = {"name": "Ries et al.", "doi": "10.6094/unifr/151460"}
    example_5 = {"name": "NFDItest", "doi": "10.5281/zenodo.8345022"}
    example_6 = {"name": "", "doi": ""}

    # database connection to load/save projects and their structure
    # dbcon = DBconnector.get_connector(project_files_root)
    # dbcon = MySQLConnector(project_files_root)
    dbcon = NullConnector(project_files_root)


    # checkout user - needed for proper manipulation of project if MySQL server is not reachable
    user_id = dbcon.checkoutUser(user_id)
    # show current saved resources of user
    dbcon.printUserInfo(user_id)

    # database connection to load/save projects and their structure
    # dbcon = DBconnector.get_connector(project_files_root)
    # dbcon = MySQLConnector(project_files_root)
    dbcon = NullConnector(project_files_root)


    # checkout user - needed for proper manipulation of project if MySQL server is not reachable
    user_id = dbcon.checkoutUser(user_id)
    # show current saved resources of user
    dbcon.printUserInfo(user_id)


    # do the use case
    # project1 = establish_new_project(dbcon, user_id, **example_1)
    # project1.keepFiles = False
    # load_id = project1.id
    # del project1
    # project2 = establish_new_project(dbcon, user_id, **example_3)
    # project2 = establish_new_project(dbcon, user_id, **example_4)

    # project3 = establish_new_project(dbcon, user_id, **example_6)
    # project3.uploadFilesFromSession("d:\\downloads\\lenz2022.zip")
    # project3.showContainerTree()
    # project3.updateDBrecord()

    load_existing_project(dbcon, user_id, 1)
    # load_project_upload_files(dbcon, user_id, 1)
    # load_existing_project(dbcon, user_id, 2)


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
    # print("max counts: {}".format(em.checkMaxCounts()))

    # EF.showSearchExpressions()
