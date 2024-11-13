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
            return project
        else:
            print(f"Project {project_id} of user {user_id} initialization failed.")

            return None

def load_project_test_concepts(dbcon, user_id, project_id):
    """
    use case function
    """
    project = load_existing_project(dbcon, user_id, project_id)
    if project is None:
        print("Can't test concepts because the project was not loaded from the storage.")
    else:
        # print(f"project files root: {project.temp_dir}")
        # show project details
        # print(str(project))

        #show paths of files and related containers
        # project.showFilesStructure()

        # upload vocabulary of concepts, methods and units from files
        # project.updateConceptsVocabularyFromFile(os.path.join(project_files_root, "test_import_concepts.json"))
        # # project.exportConceptsVocabularyToFile(project.conceptsVocabulary, os.path.join(project_files_root, "_concepts_vocabulary.json"))
        # project.updateMethodsVocabularyFromFile(os.path.join(project_files_root, "test_import_methods.json"))
        # # project.exportMethodsVocabularyToFile(project.methodsVocabulary, os.path.join(project_files_root, "_methods_vocabulary.json"))
        # project.updateUnitsVocabularyFromFile(os.path.join(project_files_root, "test_import_units.json"))
        # # project.exportUnitsVocabularyToFile(project.unitsVocabulary, os.path.join(project_files_root, "_units_vocabulary.json"))
        # # project.showConceptsVocabulary()
        # print(f"project.globalConceptsVocabulary:\n {project.globalConceptsVocabulary}")

        # # do whatever the automated crawling is capable of
        # newDataset.getCrawled()

        # and do some manual tweaking
        # like removing all concepts from container
        project.getContainerByID(776).removeAllConcepts()
        project.getContainerByID(778).removeAllConcepts()
        project.getContainerByID(776).removeAllMethods()
        project.getContainerByID(778).removeAllMethods()
        project.getContainerByID(776).removeAllUnits()
        project.getContainerByID(778).removeAllUnits()
        #
        # # assigning a concept to container
        # project.getContainerByID(776).addStringConcept(project.getContainerByID(776).name, {"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})
        #     # this one is wrong and shoouldn't be there ...
        # project.getContainerByID(778).addStringConcept(project.getContainerByID(778).name, {"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})
        # project.getContainerByID(778).addStringConcept(project.getContainerByID(778).name, {"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_36811"})
        # project.getContainerByID(778).addStringConcept(project.getContainerByID(778).name, {"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_36811"})
        # project.getContainerByID(778).addStringConcept(project.getContainerByID(778).name, {"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_4260"})
        # project.getContainerByID(778).addStringConcept(project.getContainerByID(778).name, {"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_4260"})
        #
        # # removing a concept from container
        #     # ... so it's removed
        # project.getContainerByID(778).removeConceptOfString(project.getContainerByID(778).name, {"vocabulary": "AGROVOC", "uri": "http://aims.fao.org/aos/agrovoc/c_64a2abf9"})
        #
        #
        # # assigning a method to container
        # project.getContainerByID(776).addStringMethod(project.getContainerByID(776).name, {"vocabulary": "methodic", "uri": "http://something"})
        #     # this one is wrong and shoouldn't be there ...
        # project.getContainerByID(778).addStringMethod("some method", {"vocabulary": "methodic", "uri": "somethingsomething"})
        # project.getContainerByID(778).addStringMethod("another method", {"vocabulary": "methodic", "uri": "somethingsomething2"})
        # project.getContainerByID(778).addStringMethod("and one more method", {"vocabulary": "methodic", "uri": "somethingsomethingsomething"})
        #
        # # removing a method from container
        #     # ... so it's removed
        # project.getContainerByID(778).removeMethodOfString(project.getContainerByID(778).name, {"vocabulary": "methodic", "uri": "somethingsomethingsomething"})
        #
        # # assigning a unit to container
        # project.getContainerByID(776).addStringUnit(project.getContainerByID(776).name, {"vocabulary": "unitic", "uri": "http://something"})
        #     # this one is wrong and shoouldn't be there ...
        # project.getContainerByID(778).addStringUnit(project.getContainerByID(778).name, {"vocabulary": "unitic", "uri": "[pigs per light year]"})
        # project.getContainerByID(778).addStringUnit(project.getContainerByID(778).name, {"vocabulary": "pint", "uri": "{farts*m^-3"})
        # project.getContainerByID(778).addStringUnit(project.getContainerByID(778).name, {"vocabulary": "pint", "uri": "<minions>"})
        #
        # # removing a unit from container
        #     # ... so it's removed
        # project.getContainerByID(778).removeUnitOfString(project.getContainerByID(778).name, {"vocabulary": "pint", "uri": "<minions>"})

        # crawl the dataset containers only
        ds = project.datasets[0]
        ds.removeAllConcepts()
        ds.removeAllMethods()
        ds.removeAllUnits()
        ds.getAnalyzed(cascade=True, force=True)
        ds.getCrawled(cascade=True, force=True)
        # show the datasets
        project.showDatasetsContents()

        # update database record
        project.updateDBrecord()

    return

def load_project_test_datasets(dbcon, user_id, project_id):
    """
    use case function
    """
    project = load_existing_project(dbcon, user_id, project_id)
    if project is None:
        print("Can't test datasets because the project was not loaded from the storage.")
    else:
        # print(f"project files root: {project.temp_dir}")
        # show project details
        # print(str(project))

        # remove all datasets in project
        # project.removeAllDatasets()

        # show the whole container tree
        # project.showContainerTree(show_concepts=False, show_methods=False, show_units=False)

        # CREATE AND WORK WITH DATASET
        # new empty dataset is created and added to the ResourceManager
        # newDataset = project.createDataset("TUBAF Rainfall simulations")
        # # add some containers from the ResourceManager - will be done through the GUI
        # newDataset.addContainers(project.getContainerByID([771, 956, 992]))

        # new empty dataset is created and added to the ResourceManager
        newDataset = project.createDataset("Test dataset 3")
        # add some containers from the ResourceManager - will be done through the GUI
        newDataset.addContainers(project.getContainerByID([771, 956, 992]))
        newDataset.getAnalyzed(force=True, report=False)
        newDataset.getCrawled(force=True, report=False)

        #
        # t1 = project.getContainerByID(1097)
        # t1.steps = t1.load_transformation_steps_from_file("d:\\downloads\\steps_ready2.txt")
        # t1.showContents()
        # t2 = project.getContainerByID(1132)
        # t2.showContents()
        # t3 = project.getContainerByID(1167)
        # t3.showContents()

        # # update database record
        # project.updateDBrecord()
        #
        # project.removeDataset(project.datasets[1])
        #
        # for dataset in project.datasets:
        #     dataset.showContents(show_containers=True)
        #
        ds = project.datasets[0]
        # ds.showContents()
        # ds.getAnalyzed()
        # ds.getCrawled()
        package = ds.get_frictionless_package(os.path.join(ds.directory_path, "primary_package.json"))

        ds.showContents(show_concepts=True, show_methods=False, show_units=False)

        # print(f"\npackage with concepts/methods/units:\n {package}")

        # update database record
        # project.updateDBrecord()

    return


def load_project_upload_files(dbcon, user_id, project_id):
    """
    use case function
    """
    project = load_existing_project(dbcon, user_id, project_id)
    if project is None:
        print("Can't test file upload because the project was not loaded from the storage.")
    else:
        # print(f"project files root: {project.temp_dir}")
        # show project details
        print(str(project))

        project.uploadFilesFromSession("d:\\downloads\\test_file_4.csv")
        # project.uploadFilesFromSession("d:\\downloads\\test_files.rar")
        # project.downloadFilesFromURL("https://storm.fsv.cvut.cz/data/files/p%C5%99edm%C4%9Bty/GPU/klavesove_zkratky.xlsx")

        # show the whole container tree
        project.showContainerTree()

        # show paths of files and related containers
        # project.showFilesStructure()

        # update database record
        project.updateDBrecord()
    return

def load_project_remove_container(dbcon, user_id, project_id):
    """
    use case function
    """
    project = load_existing_project(dbcon, user_id, project_id)
    if project is None:
        print("Can't test container removing because the project was not loaded from the storage.")
    else:
        # show project details
        print(str(project))

        # show the whole container tree
        project.showContainerTree()

        # remove a container from the project
        project.removeContainer(project.getContainerByID(1018))

        # show the whole container tree
        project.showContainerTree()

        # show paths of files and related containers
        # project.showFilesStructure()

        # update database record
        # project.updateDBrecord()
    return

def load_project_test_multitable(dbcon, user_id, project_id):
    """
    use case function
    """
    project = load_existing_project(dbcon, user_id, project_id)
    if project is None:
        print("Can't test multitable file analysis because the project was not loaded from the storage.")
    else:
        # show project details
        print(str(project))
        #
        # reference a container to work with
        cont = project.getContainerByID(715)
        cont.showContents()
        cont.getAnalyzed(force=True)
        # show paths of files and related containers
        # project.showFilesStructure()

        # show the whole container tree
        project.showContainerTree()

        # update database record
        project.updateDBrecord()
    return

def create_vocabulary_from_agrovoc_dump(path):
    import pickle
    # load the dump pickle
    with open(path, 'rb') as handle:
        ret = pickle.load(handle)
    # transform to vocabulary structure
    output_vocab = []
    for r in ret["results"]["bindings"]:
        output_vocab.append({"string": r["label"]["value"],
                            "concept": {"vocabulary": "AGROVOC", "uri": r["concept"]["value"]}})
    out_path = os.path.join(os.path.dirname(path), "agrovoc.json")
    # dump the result to json
    with open(out_path, "w", encoding='utf8') as f:
        json.dump(output_vocab, f, ensure_ascii=False, indent=4)
    return output_vocab

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
    # dbcon = DBconnector.get_connector()
    dbcon = MySQLConnector()
    # dbcon = NullConnector()


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

    load_project_test_datasets(dbcon, user_id, 1)
    # load_project_test_concepts(dbcon, user_id, 3)
    # load_project_upload_files(dbcon, user_id, 19)
    # load_project_remove_container(dbcon, user_id, 1)
    # load_project_test_multitable(dbcon, user_id, 3)
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
