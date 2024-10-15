# coding = utf-8
# -*- coding: utf-8 -*-

import requests
import os
import sys
import shutil
import json
from pathlib import Path

from .metadata_scheme import MetadataStructureMap
from .db_access import DBconnector
from .exceptions import DOIdataRetrievalException, LocalFileManipulationError, ContainerStructureError, DatabaseEntryError, NameNotUniqueError, DatabaseFetchError, DeserializationError

# general variables
doi_metadata_key = "DOI metadata"
publisher_metadata_key = "Publisher metadata"


class ProjectManager:
    """
    Top level manager of metadata mining project.
    Gathers all source files either from remote sources (download from URL) or local sources (upload from local computer).

    """

    def __init__(self, db_connection, user_id, **kwargs):
        self.initialized = False

        self.dbconnection = db_connection
        self.ownerID = user_id
        self.name = kwargs.get("name")

        self.doi = kwargs.get("doi")

        # registration agency of the DOI
        self.registrationAgency = None
        # container with metadata package from DOI record
        self.DOImetadata = None
        # container with metadata package from Publisher
        self.publisherMetadata = None
        # publisher instance
        self.publisher = None
        # list of files that were published with the resource - publicly available through url
        self.publishedFiles = []
        # list of files that were downloaded
        self.downloadedFiles = []
        # list of files that were uploaded from session
        self.uploadedFiles = []
        # the tree structure of included files and other container types
        self.containerTree = []
        # dictionary of file paths and related container IDs - useful for cross-checking between files and containers
        self.containersOfPaths = {}
        # language of the project
        self.language = None

        # project concepts vocabulary
        self.conceptsVocabulary = {}
        # project methods vocabulary
        self.methodsVocabulary = {}
        # project units vocabulary
        self.unitsVocabulary = {}

        # global concepts vocabulary
        self.globalConceptsVocabulary = self.loadConceptsVocabularyFromFile(self.dbconnection.global_concepts_vocabulary)
        # global methods vocabulary
        self.globalMethodsVocabulary = self.loadMethodsVocabularyFromFile(self.dbconnection.global_methods_vocabulary)
        # global units vocabulary
        self.globalUnitsVocabulary = self.loadUnitsVocabularyFromFile(self.dbconnection.global_units_vocabulary)


        # dedicated directory for file saving
        self.temp_dir = None
        # for now - some kind of licences definition and appropriate actions should be implemented
        self.keepFiles = False

        # project's own ContainerHandlerFactory to keep track of containers
        self.containerFactory = ContainerHandlerFactory()
        # the crawlers factory
        self.crawlerFactory = CrawlerFactory()

        # list of Dataset class instances existing within this project
        self.datasets = []

        # if ID is None establish a new project on the storage
        if kwargs.get("id") is None:
            try:
                self.id, self.temp_dir = self.dbconnection.establishProjectRecord(user_id, self)
            except DatabaseEntryError as e:
                print("Failed to establish new Project record in the SoilPulse database.")
                raise
            except NameNotUniqueError:
                print(f"Project with name \"{kwargs.get('name')}\" already exists. Use unique names for your projects!")
            else:
                self.keepFiles = True
                self.initialized = True
                self.setDOI(kwargs.get("doi"))

        else:
            # load the existing project properties from the database
            self.id = kwargs.get("id")
            try:
                self.dbconnection.loadProject(self)
            except DatabaseFetchError as e:
                # this should never happen as the ID will be obtained by query from the DB ...
                print(f"\n\nERROR LOADING PROJECT")
                print(e.message)
                self.initialized = False
            except DeserializationError as e:
                # this could happen quite easily while using files to store ...
                print(f"\n\nERROR LOADING PROJECT")
                print(e.message)
                self.initialized = False
            else:
                self.initialized = True
        return


    def __del__(self):
        if self.initialized:
            if hasattr(self, "keepFiles"):
                if not self.keepFiles:
                    print(f"\n\nDeleting project files because we can't keep them :-(")
                    failed = self.deleteDownloadedFiles()
                    if len(failed) > 0:
                        print(f"following files couldn't be deleted:")
                        for f in failed:
                            print(f"\t{f}")

    def __str__(self):
        out = f"\n=== Project #{self.id} {70 * '='}\n"
        out += f"name: {self.name}\n"
        out += f"local directory: {self.temp_dir}\n"
        out += f"keep stored files: {'yes' if self.keepFiles else 'no'}\n"
        out += f"space occupied: {get_formated_file_size(self.temp_dir)}\n"
        out += f"DOI: {self.doi}\n" if self.doi is not None else f"no DOI assigned\n"
        out += f"{90 * '='}\n"
        return out

    def updateDBrecord(self, cascade=True):
        """
        Saves current state of the project and its contents (if specified) through current DBconnector object

        :param cascade: whether to save the containers, datasets and other state attributes
        """
        print(f"\nSaving project \"{self.name}\" with ID {self.id} ... ")
        self.dbconnection.updateProjectRecord(self, cascade)
        print(f" ... successful.")
        return

    def getContainersSerialization(self):
        """
        Collects serialization JSON structure of all containers in the tree
        :return: dictionary with all containers attributes
        """
        cont_dict = {}
        for cont in self.containerTree:
            cont_dict.update({cont.id: cont.getSerializationDictionary()})
        return cont_dict

    def getDatasetsSerialization(self):
        """
        Collects serialization JSON structure of all datasets in the project
        :return: dictionary with all datasets attributes
        """
        dataset_list = []
        for dataset in self.datasets:
            dataset_list.append(dataset.getSerializationDictionary())
        return dataset_list


    def setDOI(self, doi):
        """
        Changes the DOI of a project with all appropriate actions
        - reads the registration agency and publisher response metadata and assigns them to the ProjectManager
        - check for files bound to the DOI record
        - download the files (unpack archives if necessary)
        - create container tree from files
        - remove old files if there were any

        """
        print(f"doi: '{doi}'")
        # if the doi parameter already had some value
        if self.doi:
            # and the new value differs from the previous one
            if self.doi != doi:
                # remove the files that were downloaded from the DOI record before
                self.deleteAllProjectFiles()
                pass

        if doi is not None and doi != "":
            # set the new DOI
            self.doi = doi
            # populate the registration agency
            self.registrationAgency = ProjectManager.getRegistrationAgencyOfDOI(doi)
            # populate the metadata properties
            self.DOImetadata = self.getDOImetadata(doi)
            # append the DOI metadata JSON container to the ProjectManagers containers
            DOIcont = self.containerFactory.createHandler("json", name=doi_metadata_key, project_manager=self, parent_container=None, content=self.DOImetadata, path=None)
            self.containerTree.append(DOIcont)
            DOIcont.saveAsFile(self.temp_dir, doi_metadata_key.replace(" ", "_")+".json")

            # populate publisher with Publisher class instance
            try:
                self.publisher = self.getPublisher(self.DOImetadata)
            except NotImplementedError:
                print("Publisher instance could not be created:")
                print("No other data publisher than Zenodo implemented so far.")
            else:
                self.publisherMetadata = self.getPublisherMetadata()

                # append the publisher metadata JSON container to the ProjectManagers containers
                publisherCont = self.containerFactory.createHandler("json", name=publisher_metadata_key, project_manager=self, parent_container=None, content=self.publisherMetadata, path=None)
                self.containerTree.append(publisherCont)
                publisherCont.saveAsFile(self.temp_dir, publisher_metadata_key.replace(" ", "_")+".json")

                # get downloadable files information from publisher
                self.publishedFiles = self.publisher.getFileInfo()
        else:
            return
        return

    def getAllFilesList(self):
        """
        Collects file paths from all containers in the tree
        """
        filesList = []
        for cont in self.containerTree:
            cont.listOwnFiles(filesList)
        return filesList

    def deleteAllProjectFiles(self):
        """
        Deletes files of all containers in the tree
        """
        failed = []
        for cont in self.containerTree:
            cont.deleteOwnFiles(failed)
        if len(failed) > 0:
            flist = "\n".join([f"{f[0]}: {f[1]}" for f in failed])
            raise LocalFileManipulationError(f"Failed to delete following files:\n{flist}")
        else:
            print("All files successfully deleted.")
        return failed

    def deleteDownloadedFiles(self):
        failed = []
        for f in self.downloadedFiles[:]:
            if os.path.isfile(f):
                try:
                    os.remove(f)
                    self.downloadedFiles.remove(f)
                except PermissionError as e:
                    failed.append(f)
                    print(f)
            if os.path.isdir(f):
                try:
                    os.rmdir(f)
                    self.downloadedFiles.remove(f)
                except PermissionError as e:
                    failed.append(f)
                    print(f)
        if len(failed) > 0:
            flist = "\n".join([f for f in failed])
            raise LocalFileManipulationError(f"Failed to delete following files:\n{flist}")
        else:
            print("All downloaded files successfully deleted.")
        return failed

    def deleteUploadedFiles(self):
        failed = []
        for f in self.uploadedFiles[:]:
            if os.path.isfile(f):
                try:
                    os.remove(f)
                    self.uploadedFiles.remove(f)
                except PermissionError as e:
                    failed.append(f)
                    print(f)

            if os.path.isdir(f):
                try:
                    os.rmdir(f)
                    self.uploadedFiles.remove(f)
                except PermissionError as e:
                    failed.append(f)
                    print(f)
        if len(failed) > 0:
            flist = "\n".join([f for f in failed])
            raise LocalFileManipulationError(f"Failed to delete following files:\n{flist}")
        else:
            print("All uploaded files successfully deleted.")
        return failed

    def getPublisher(self, DOI_metadata):
        """
        Gets the Publisher instance from the DOI metadata
        """
        if not DOI_metadata:
            try:
                DOImetadata = self.getDOImetadata(self.__doi)
            except DOIdataRetrievalException as e:
                print("Error occurred while retrieving DOI record metadata.")
                print(e.message)
                return None
        else:
            try:
                publisherKey = DOI_metadata['data']['attributes']['publisher']
            except AttributeError as e:
                print("Couldn't find publisher value in the DOI registration agency metadata response.")
                print(e.message)
            else:
                if publisherKey == "Zenodo":
                    zenodo_id = DOI_metadata['data']['attributes']['suffix'].split(".")[-1]
                    publisher = PublisherFactory.createHandler(publisherKey, zenodo_id)
                    return publisher
                else:
                    raise NotImplementedError()

    @staticmethod
    def getRegistrationAgencyOfDOI(doi, meta=False):
        """
        Get registration agency from doi.org API.

        :param doi: the DOI string of a published dataset (10.XXX/XXXX).
        :param meta: true to return whole json, false to return only a string of registration agency

        :return: complete registration agency json if meta = True, else registration agency name string
        """
        url = "https://doi.org/ra/" + doi
        try:
            # print("obtaining DOI registration agency ...")
            RAjson = requests.get(url).json()
        except requests.exceptions.ConnectionError:
            raise DOIdataRetrievalException("A connection error occurred while getting registration agency of provided DOI. Check your internet connection.")
        except requests.exceptions.Timeout:
            raise DOIdataRetrievalException("The request timed out while getting registration agency of provided DOI.")
        except requests.exceptions.HTTPError as e:
            raise DOIdataRetrievalException("HTTP Error occured while getting registration agency of provided DOI:", e)
        except requests.exceptions.RequestException as e:
            raise DOIdataRetrievalException("An unknown error occurred while getting registration agency of provided DOI:", e)
        else:
            if 'status' in RAjson[0].keys():
                if RAjson[0]['status'] == "Invalid DOI":
                    raise DOIdataRetrievalException(f"provided DOI '{doi}' is invalid.")
                if RAjson[0]['status'] == "DOI does not exist":
                    raise DOIdataRetrievalException(f"provided DOI '{doi}' is not registered.")
            else:
                if (meta):
                    return RAjson
                else:
                    return RAjson[0]['RA']



    @staticmethod
    def getDOImetadata(doi):
        """
        Get metadata in JSON from registration agency for provided DOI

        :param doi: doi string of the resource
        :return: json of metadata
        """
        # TODO implement other metadata providers
        RA = ProjectManager.getRegistrationAgencyOfDOI(doi)
        if (RA == 'DataCite'):
            url = "https://api.datacite.org/dois/" + doi
            headers = {"accept": "application/vnd.api+json"}

            try:
                print("\nObtaining metadata from DOI registration agency ...")
                output = requests.get(url, headers=headers).json()

            except requests.exceptions.ConnectionError:
                print(" A connection error occurred. Check your internet connection.")
            except requests.exceptions.Timeout:
                print(" The request timed out.")
            except requests.exceptions.HTTPError as e:
                print(" HTTP Error:", e)
            except requests.exceptions.RequestException as e:
                print(" An error occurred:", e)
            else:
                if 'error' in output.keys():
                    raise DOIdataRetrievalException(f"Registration agency '{ProjectManager.getRegistrationAgencyOfDOI(doi)}' didn't respond. Error {output['status']}: {output['error']}")
                print(" ... successful\n")
                return output
        else:
            print("Unsupported registration agency '{}'".format(RA))
            raise DOIdataRetrievalException(f"Unsupported registration agency '{RA}'")

    def getPublisherMetadata(self):
        return self.publisher.getMetadata()

    def downloadPublishedFiles(self, list = None, unzip=True):
        """
        Download files that are stored in self.sourceFiles dictionary

        :param list: list of SourceFile indexes to be downloaded, or None if files are to be downloaded
        :param unzip: if the downloaded file is a .zip archive it will be extracted if unzip=True
        :return: list of local relative paths of all files copied to the local/temporary storage
        """
        if self.publishedFiles is not None:
            if len(self.publishedFiles) == 0:
                print("The list of published files is empty.\n")
            else:
                # create the target directory if not exists
                print("downloading remote files to SoilPulse storage ...")

                fileList = []
                if not list:
                    for sourceFile in self.publishedFiles:
                        url = sourceFile.source_url
                        # any file name manipulation can be performed here
                        filename = sourceFile.filename.replace("\\/<[^>]*>?", "_")

                        local_path = os.path.join(self.temp_dir, filename)

                        try:
                            response = requests.get(url+"/content")
                        except requests.exceptions.ConnectionError:
                            print("\tA connection error occurred while trying to download published files - check your internet connection.")
                            return False
                        except requests.exceptions.Timeout:
                            print("\tThe request timed out while trying to download published files.")
                            return False
                        except requests.exceptions.HTTPError as e:
                            print("\tHTTP Error occurred while trying to download published files:\n", e)
                            return False
                        except requests.exceptions.RequestException as e:
                            print("\tRequest Error occurred while trying to download published files:\n", e)
                            return False
                        else:
                            if response.ok:
                                with open(local_path, mode="wb") as filesave:
                                    filesave.write(response.content)

                                # on success save local path of downloaded file to its attribute
                                sourceFile.local_path = local_path
                                fileList.append(local_path)

                                # create new container from the file with all related actions
                                newContainer = self.containerFactory.createHandler('filesystem', self, None, name=sourceFile.filename, path=local_path)
                                self.containerTree.append(newContainer)

                            else:
                                # something needs to be done if the response is not OK ...
                                print("\t\tThe response was not OK!")
                                sourceFile.local_path= None

                                return False

                print(" ... successful\n")
                self.downloadedFiles.extend(fileList)
                return fileList
        else:
            raise DOIdataRetrievalException("List of files from DOI record was not retrieved correctly.")


    def uploadFilesFromSession(self, files):
        """
        Handles all needed steps to upload files from a session (unpack archives if necessary) and create file structure tree
        """
        if not isinstance(files, list):
            files = [files]
        for file in files:
            filename = os.path.basename(file)
            target_file_path = os.path.join(self.temp_dir, filename)
            shutil.copyfile(file, target_file_path)
            # create new container from the file with all related actions
            newContainer = self.containerFactory.createHandler('filesystem', self, None, name=filename,
                                                               path=target_file_path, cascade=True)
            self.containerTree.append(newContainer)
            # add new file path to uploaded files list
            self.uploadedFiles.append(newContainer.path)

        return

    def getContainerByID(self, cid):
        if isinstance(cid, list):
            try:
                return [self.containerFactory.getContainerByID(c) for c in cid]
            except:
                raise
        else:
            return self.containerFactory.getContainerByID(cid)

    def getContainersByParentID(self, pid):
        """
        Return container instances that have parent container with given ID

        :param pid: ID of the parent container
        """
        return self.getContainerByID(pid).containers

    def createDataset(self, name, id=None):
        """
        Adds Dataset object instance to dataset list
        """
        if id is None:
            # find next ID to assign
            id = 0
            if self.datasets is not None:
                for ds in self.datasets:
                    id = max(id, ds.id)
                id += 1
            else:
                self.datasets = []
                id = 1
        else:
            for dataset in self.datasets:
                if dataset.id == id:
                    print(f"Can't create dataset because the project {self.id} already contains dataset with ID {id}")
                    return None
        # create the dataset and assign ID
        new_dataset = Dataset(name, self)
        new_dataset.id = id
        # append the dataset to the list of the project
        self.datasets.append(new_dataset)

        return new_dataset

    def removeDataset(self, item):
        """
        Removes Dataset object instance from dataset list
        """

        try:
            did = self.datasets[item].id
            dname = self.datasets[item].name
            # remove record from DB
            self.dbconnection.deleteDatasetRecord(self.datasets[item])
            # remove dataset from the list
            del self.datasets[item]

        except IndexError:
            print(f"Can't remove dataset {item} - project {self.id} has only {len(self.datasets)} datasets.")
        else:
            print(f"dataset #{did} - '{dname}' was deleted from project")
        return


    def showContainerTree(self):
        """
        Induces printing contents of the whole container tree
        """
        print("\n" + 80 * "=")
        print(f"{self.name}\ncontainer tree:")
        print(80 * "-")
        for container in self.containerTree:
            container.showContents(0)
        print(80 * "=" + 2 * "\n")


    def showDatasetsContents(self, show_containers=True):
        """
        Induces printing contents of all dataset in project

        """
        for ds in self.datasets:
            ds.showContents(show_containers=show_containers)
        return

    def showFilesStructure(self):
        """
        Prints "file path" - "container ID" mapping for all containers in the project
        """

        print("\n" + 80 * "-")
        print(f"{self.name}\nfile paths and related container IDs:")
        print(80 * "-")
        for path, contID in self.containersOfPaths.items():
            print(f"{path}\t[{contID}]")

    def collectAllConcepts(self):
        """
        Collects all concepts from containers of the tree
        """
        project_concepts = {}
        for cont in self.containerTree:
            all_containers_concepts = cont.collectConcepts({}, True)
            if len(all_containers_concepts) > 0:
                updateVocabulary(project_concepts, all_containers_concepts)
        return project_concepts

    def collectAllMethods(self):
        """
        Collects all methods from containers of the tree
        """
        project_methods = {}
        for cont in self.containerTree:
            all_containers_methods = cont.collectMethods({}, True)
            if len(all_containers_methods) > 0:
                updateVocabulary(project_methods, all_containers_methods)
        return project_methods

    def collectAllUnits(self):
        """
        Collects all units from containers of the tree
        """
        project_units = {}
        for cont in self.containerTree:
            all_containers_units = cont.collectUnits({}, True)
            if len(all_containers_units) > 0:
                updateVocabulary(project_units, all_containers_units)
        return project_units

    def updateConceptsVocabularyFromContents(self):
        """
        Updates projects string-concept translations by translations from own containers
        """
        concepts_of_containers = self.collectAllConcepts()
        updateVocabulary(self.conceptsVocabulary, concepts_of_containers)
        return

    def updateMethodsVocabularyFromContents(self):
        """
        Updates projects string-concept translations by translations from own containers
        """
        methods_of_containers = self.collectAllMethods()
        updateVocabulary(self.methodsVocabulary, methods_of_containers)
        return

    def updateUnitsVocabularyFromContents(self):
        """
        Updates projects string-concept translations by translations from own containers
        """
        units_of_containers = self.collectAllUnits()
        updateVocabulary(self.unitsVocabulary, units_of_containers)
        return
    def updateConceptsVocabularyFromFile(self, input_file):
        """
        Adds string-concepts translations to project's vocabulary (if not already there) from specified file
        """
        # load the input JSON file to vocabulary
        str_conc_dict = self.loadConceptsVocabularyFromFile(input_file)
        updateVocabulary(self.conceptsVocabulary, str_conc_dict)
        # no need to save the vocabulary to file as it is saved when project is saved
        return

    def updateMethodsVocabularyFromFile(self, input_file):
        """
        Adds string-method translations to project's vocabulary (if not already there) from specified file
        """
        # load the input JSON file to vocabulary
        str_meth_dict = self.loadMethodsVocabularyFromFile(input_file)
        updateVocabulary(self.methodsVocabulary, str_meth_dict)
        # no need to save the vocabulary to file as it is saved when project is saved
        return

    def updateUnitsVocabularyFromFile(self, input_file):
        """
        Adds string-concepts translations to project's vocabulary (if not already there) from specified file
        """
        # load the input JSON file to vocabulary
        str_unit_dict = self.loadUnitsVocabularyFromFile(input_file)
        updateVocabulary(self.unitsVocabulary, str_unit_dict)
        # no need to save the vocabulary to file as it is saved when project is saved
        return

    def loadVocabularyFromFile(self, input_file, type):
        """
        Loads string- translations JSON file

        :param input_file: path of vocabulary file to load from
        :param type: type of vocabulary 'concept'/'method'/'unit'
        """

        # load the input JSON file
        str_dict = {}
        with open(input_file, 'r') as f:
            for str in json.load(f):
                str_dict.update({str['string']: str[type]})
        return str_dict

    def loadConceptsVocabularyFromFile(self, input_file):
        """
        Loads string-concepts translations JSON file
        """
        return self.loadVocabularyFromFile(input_file, 'concept')

    def loadMethodsVocabularyFromFile(self, input_file):
        """
        Loads string-method translations JSON file
        """
        return self.loadVocabularyFromFile(input_file, 'method')

    def loadUnitsVocabularyFromFile(self, input_file):
        """
        Loads string-unit translations JSON file
        """
        return self.loadVocabularyFromFile(input_file, 'unit')

    def updateGlobalConceptsVocabularyFromProject(self):
        """
        Adds string-concepts translations from project's vocabulary to global vocabulary if not already there
        """
        # global string-concept translations file path
        vocabulary_file = os.path.join(self.dbconnection.project_files_root, self.dbconnection.concepts_vocabulary_filename)
        # load the JSON file to vocabulary structure
        target_vocabulary = self.loadConceptsVocabularyFromFile(vocabulary_file)

        updateVocabulary(target_vocabulary, self.conceptsVocabulary)
        self.exportConceptsVocabularyToFile(vocabulary_file)
        return

    def exportConceptsVocabularyToFile(self, vocabulary, filepath):
        """
        Saves string-concepts vocabulary to a file
        """
        output_data = []
        for string, concepts in vocabulary.items():
            output_data.append({"string": string, "concept": [{"vocabulary": concept['vocabulary'], "uri": concept['uri']} for concept in concepts]})
        with open(filepath, "w") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)


    def showConceptsVocabulary(self):
        print(f"\nString-concept vocabulary of project #{self.id}:")
        for string, concepts in self.conceptsVocabulary.items():
            print(f"\"{string}\"")
            for concept in concepts:
                print(f"\t{concept}")
        print("\n")

class Dataset:
    """
    Represents a set of data containers that form together a distinct collection of data represented by a MetadataStructureMap.
    The instance has its own MetadataStructureMap that is being composed during the metadata generation phase
    """

    def __init__(self, name, project):
        # dataset id
        self.id = None
        # dataset name
        self.name = name
        # project reference
        self.project = project
        # container object instances that the dataset consists of
        self.containers = []
        # the instance of the metadata mapping
        self.metadataMap = MetadataStructureMap()


    def addContainers(self, containers):
        """
        Adds one or more ContainerHandler instances to Dataset's containers list
        """
        if isinstance(containers, list):
            for cont in containers:
                self.addContainer(cont)
        else:
            self.addContainer(containers)
        return

    def addContainer(self, container):
        for existing in self.containers:
            if container.id == existing.id:
                return
        self.containers.append(container)
        return

    def removeContainer(self, containers_to_remove):
        """
        Removes one or more ContainerHandler instances from Dataset's containers list
        """
        if not isinstance(containers_to_remove, list):
            containers_to_remove = [containers_to_remove]
        self.containers = [con for con in self.containers if con not in containers_to_remove]
        return

    def updateDBrecord(self, db_connection):
        print(f"\tupdating dataset '{self.name}' ... ")
        db_connection.updateDatasetRecord(self)
        return

    def getContainerIDsList(self):
        return [c.id for c in self.containers]

    def showContents(self, show_containers=True):
        print(f"\n==== {self.name} " + 60 * "=" + f" #{self.id}")

        if show_containers:
            self.showContainerTree()
        print(80 * "=" + "\n")

    def showContainerTree(self):
        """
        Induces printing contents of the dataset's container tree
        """
        print(f"---- container tree: ----")
        for container in self.containers:
            container.showContents(0)

    def getSerializationDictionary(self):
        return {"id": self.id, "name": self.name, "container IDs": [c.id for c in self.containers]}


    def checkMetadataStructure(self):
        self.metadataMap.checkConsistency()

    def getCrawled(self):
        for container in self.containers:
            container.getCrawled()

class SourceFile:
    def __init__(self, id, filename, size = None, source_url = None, checksum = None, checksum_type = None):
        self.id = id
        self.filename = filename
        self.source_url = source_url

        self.size = size
        self.checksum = checksum
        self.checksum_type = checksum_type

        self.local_path = None

class ContainerHandlerFactory:
    """
    ContainerHandler object instances factory, the only way to create container handlers
    Each Project has one to keep track of all the ContainerHandler class and all subclass' instances created
    """

    # directory of registered container types subclasses
    containerTypes = {}

    @classmethod
    def registerContainerType(cls, containerTypeClass, key):
        """
        Registers ContainerHandler subclasses in the factory
        """
        cls.containerTypes[key] = containerTypeClass
        print("Container type '{}' registered".format(key))
        return

    @classmethod
    def getAllNeededDBfields(cls):
        needed_fields = []
        for key, typeClass in cls.containerTypes.items():
            for fieldname in typeClass.DBfields.keys():
                needed_fields.append(fieldname)
        return needed_fields

    def __init__(self):

        # dictionary of already created container handlers by ID
        self.containers = {}
        # class counter of ID that was assigned to last created ContainerHandler
        self.lastContainerID = 0


    def createHandler(self, general_type, *args, **kwargs):
        """
        Creates and returns instance of ContainerHandler of given type
        Subclasses can implement further specialization of the type by overriding ContainerHandler.getSpecializedSubclassType()

        """
        # check if the requested container type is registered in the factory
        if general_type not in ContainerHandlerFactory.containerTypes.keys():
            raise ValueError("Unsupported container handler type '{}'. Supported are:"
                             " {}".format(general_type, ",".join( ["'" + k + "'" for k in self.containerTypes.keys()])))
        else:
            # if 'id' is in kwargs and is not None - e.a. loading the container from DB
            if kwargs.get("id") is not None:
                # check if the value is not present in already existing containers of this factory
                if kwargs["id"] not in self.containers.keys():
                    self.lastContainerID = max(kwargs["id"], self.lastContainerID)
                else:
                    print(f"Container IDs produced so far:")
                    for id, cont in self.containers.items():
                        print(f"{id} - {cont.name}")
                        # print(f"{id} - {cont.name} ({cont.type})")
                    raise ContainerStructureError(f"This container factory has already produced container "\
                                                f"with ID {kwargs['id']} (name: '{self.containers.get(kwargs['id']).name}')")

            # else use the inner counter to assign ID
            else:
                self.lastContainerID += 1
                kwargs.update({"id": self.lastContainerID})


            if kwargs.get("type") is not None:
                # if 'type' is in kwargs and is not None - e.a. loading the container from DB
                specialized_type = kwargs.pop("type")
            else:
                # get specialized subclass type
                specialized_type = self.containerTypes[general_type].getSpecializedSubclassType(**kwargs)
                # check if the requested specialized container type is registered in the factory
                if specialized_type not in ContainerHandlerFactory.containerTypes.keys():
                    raise ValueError("Unsupported container handler type '{}'. Supported are:"
                                     " {}".format(general_type, ",".join(["'" + k + "'" for k in self.containerTypes.keys()])))

                # create new container instance with unique id in the ProjectManager scope
            new_container = self.containerTypes[specialized_type](*args, **kwargs)
            # put it in the factory list
            self.containers.update({new_container.id: new_container})
            return new_container

    def getContainerByID(cls, cid):
        """
        Returns container of particular ID from inner dictionary
        """

        if cls.containers.get(cid) is not None:
            return cls.containers.get(cid)
        else:
            raise ContainerStructureError(f"Container id = {cid} was never created by this factory!")

class ContainerHandler:
    """
    Represents an enclosed data structure.
    It can be either a file or string or other data structure that can be manipulated and analyzed
    """
    containerType = None
    containerFormat = None
    keywordsDBname = None

    # dictionary of DB fields needed to save this subclass instance attributes
    DBfields = {}
    # dictionary of attribute names to be used for DB save/update - current values need to be obtained at right time before saving
    serializationDict = {}

    @classmethod
    def getSpecializedSubclassType(cls, **kwargs):
        """
        This method comes handy when one ContainerHandler subclass needs to control some rules for creation of own subclasses
        Default is 'no specialization' e.a. returns the same type as is
        """
        return cls.containerType

    def __init__(self, project, parent_container, **kwargs):
        # unique ID in the project scope
        self.id = kwargs["id"]
        # container name (filename/database name/table name ...)
        self.name = kwargs.get("name")
        # reference to the ProjectManager that the container belongs to
        self.project = project
        # parent container instance (if not root container)
        self.parentContainer = parent_container
        # data containers that the container contains
        self.containers = []
        # metadata entities that the container contains
        self.metadataElements = []
        # the crawler assigned to the container
        self.crawler = None
        # was crawled flag
        self.wasCrawled = False
        # was analyzed flag
        self.isAnalyzed = False

        # dictionary of string-concept translations {the string: [{"vocabulary": vocabulary provider, "uri": URI of the concept}, ...]
        self.concepts = kwargs.get("concepts") if kwargs.get("concepts") is not None else {}
        # dictionary of string-method translations {the string: [{"vocabulary": vocabulary provider, "uri": URI of the method}, ...]
        self.methods = kwargs.get("methods") if kwargs.get("methods") is not None else {}
        # dictionary of string-unit translations {the string: [{"vocabulary": vocabulary provider, "uri": URI of the unit}, ...]
        self.units = kwargs.get("units") if kwargs.get("units") is not None else {}

    def __str__(self):
        out = f"\n|  # {self.id}  |  name: '{self.name}'  \n|  type: {type(self).__name__}  |  parent: "
        out += f"{self.parentContainer.id}\n" if self.parentContainer is not None else f"project root\n"
        if hasattr(self, "path"):
            out += f"|  {self.path}\n"
        if hasattr(self, "concepts"):
            out += f"|  string-concept translations:"
            for string, concs in self.concepts.items():
                out += f"|\t\"{string}\""
                for conc in concs:
                    out += f"|\t\t{concs}"
        if hasattr(self, "methods"):
            out += f"|  concepts: {', '.join([meth['uri']+' ('+meth['vocabulary']+')' for meth in self.methods])}"
        if hasattr(self, "units"):
            out += f"|  units: {', '.join([unit['uri']+' ('+unit['vocabulary']+')' for unit in self.units])}\n"
        return out


    def showContents(self, depth = 0, ind = ". ", show_concepts=True, show_methods=True, show_units=True):
        """
        Prints structured info about the container and invokes showContents on all of its containers

        :param depth: current depth of showContent recursion
        :param ind: string of a single level indentation
        :param show_concepts: whether to show also the string-concepts translations
        :param show_methods: whether to show also the string-methods translations
        :param show_units: whether to show also the string-units translations
        """
        # get the indentation string
        t = ind * depth
        # print attributes of this container
        pContID = self.parentContainer.id if self.parentContainer is not None else "root"
        # print(f"{t}{self.id} - {self.name} ({self.containerType}) [{len(self.containers)}] {'{'+self.crawler.crawlerType+'}'}  >{pContID}")
        print(f"{t}{self.id} - {self.name} ({self.containerType}) [{len(self.containers)}] >{pContID}")
        if show_concepts:
            if hasattr(self, "concepts"):
                for string, concepts in self.concepts.items():
                    print("  "*(depth+1)+string+": "+"; ".join([f"'{conc['uri']}' ('{conc['vocabulary']}')'" for conc in concepts]))

        if show_methods:
            if hasattr(self, "methods"):
                for string, methods in self.methods.items():
                    print("  "*(depth+1)+string+": "+"; ".join([f"'{meth['uri']}' ('{meth['vocabulary']}')'" for meth in methods]))

        if show_units:
            if hasattr(self, "units"):
                for string, units in self.units.items():
                    print("  "*(depth+1)+string+": "+"; ".join([f"'{unit['uri']}' ('{unit['vocabulary']}')'" for unit in units]))

        # invoke showContents of sub-containers
        if len(self.containers) > 0:
            depth += 1
            for cont in self.containers:
                cont.showContents(depth)

    def updateDBrecord(self, db_connection, cascade=True):
        """
        Invokes updating of containers record in storage
        """
        db_connection.updateContainerRecord(self, cascade)
        return

    def getSerializationDictionary(self, cascade=True):
        """
        Creates JSON structured string with serialization of the container and its sub-containers

        :param cascade: whether to recurse through sub-containers
        """
        # general properties of all containers
        dict = {"id": self.id,
                "type": self.containerType,
                "name": self.name,
                "parent_id_local": self.parentContainer.id if self.parentContainer is not None else None,
                "crawler_type": self.crawler.crawlerType if self.crawler is not None else None}

        # type-specific properties
        for key, attr_name in self.serializationDict.items():
            dict.update({key: str(getattr(self, attr_name))})

        # concepts
        if self.concepts is not None:
            dict.update({"concepts": self.concepts})
        else:
            dict.update({"concepts": {}})
        # units
        if hasattr(self, "units"):
            if self.units is not None:
                dict.update({"units": self.units})
            else:
                dict.update({"units": {}})
        # methods
        if hasattr(self, "methods"):
            if self.methods is not None:
                dict.update({"methods": self.methods})
            else:
                dict.update({"methods": {}})

        # and recursion for the sub-containers
        if cascade:
            sub_conts = {}
            for cont in self.containers:
                sub_conts.update({cont.id: cont.getSerializationDictionary()})
            dict.update({"containers": sub_conts})
        return dict

    def collectContainerIDsToList(self, output=[]):
        """
        Collects recursively IDs of all sub-containers (and their sub-containers ...)

        :param output: the output list of all sub-container IDs
        """

        output.append(self.id)
        for cont in self.containers:
            cont.collectContainerIDsToList(output)
        return output


    def createTree(self, *args):
        pass

    def getAnalyzed(self):
        """Induces further decomposition of the container into logical sub-elements."""
        pass

    def getCrawled(self, cascade):
        """Induces content search for metadata elements based on appropriate set of search rules and terms."""
        pass

    def assignCrawler(self, crawler):
        self.crawler = crawler

    def listOwnFiles(self, collection):
        pass

    def addStringConcept(self, string, concept):
        """
        Add string to concept translation to container while checking for duplicity with already present concepts

        :param string: string to be assigned the concept translation
        :param concept: concept to be added
        :return: None
        """
        print(f"adding concept {concept} of string '{string}'")

        # get all concepts assigned to the input string
        this_string_concepts = self.concepts.get(string)
        # if the string has no concept assigned yet
        if this_string_concepts is None:
            self.concepts.update({string: [concept]})
        # otherwise check for new concept duplicity with already assigned concepts
        else:
            is_there = False
            for existing_concept in this_string_concepts:
                if existing_concept["vocabulary"] == concept["vocabulary"] and existing_concept["uri"] == concept["uri"]:
                    is_there = True
            if not is_there:
                this_string_concepts.append(concept)
        return

    def addStringMethod(self, string, method):
        """
        Add string to method translation to container while checking for duplicity with already present methods

        :param string: string to be assigned the method translation
        :param method: method to be added
        :return: None
        """
        print(f"adding method {method} of string '{string}'")
        # get all methods assigned to the input string
        this_string_methods = self.methods.get(string)
        # if the string has no method assigned yet
        if this_string_methods is None:
            self.methods.update({string: [method]})
        # otherwise check for new method duplicity with already assigned method
        else:
            is_there = False
            for existing_method in this_string_methods:
                if existing_method["vocabulary"] == method["vocabulary"] and existing_method["uri"] == method["uri"]:
                    is_there = True
            if not is_there:
                this_string_methods.append(method)
        return

    def addStringUnit(self, string, unit):
        """
        Add string to unit translation to container while checking for duplicity with already present methods

        :param string: string to be assigned the unit translation
        :param unit: unit to be added
        :return: None
        """
        print(f"adding unit {unit} of string '{string}'")

        # get all methods assigned to the input string
        this_string_units = self.units.get(string)
        # if the string has no method assigned yet
        if this_string_units is None:
            self.units.update({string: [unit]})
        # otherwise check for new unit duplicity with already assigned unit
        else:
            is_there = False
            for existing_unit in this_string_units:
                if existing_unit["vocabulary"] == unit["vocabulary"] and existing_unit["uri"] == unit["uri"]:
                    is_there = True
            if not is_there:
                this_string_units.append(unit)
        return

    def removeConceptOfString(self, string, concept_to_remove):
        """
        Remove string-concept translation from container.
        If the translation was last for given string, the string gets removed from the translations as well.

        :param string: string that has the concept assigned
        :param concept_to_remove: concept to be removed
        :return: None if the string was not in the containers string-concept translations
                0 if the string translations was empty and the string was removed from the translations
                1 on successful removal of the concept from
        """

        if self.concepts.get(string) is None:
            print(f"\tString '{string}' is not present in string-concept translations of container {self.id}")

        else:
            remi = None
            print(f"removing concept {concept_to_remove} of string '{string}'")
            i = 0
            for concepts_of_string in self.concepts.get(string):
                # print(concepts_of_string)
                if concepts_of_string["vocabulary"] == concept_to_remove["vocabulary"] and concepts_of_string["uri"] == concept_to_remove["uri"]:
                    remi = i
                i += 1
            if remi is not None:
                del(self.concepts.get(string)[remi])
                print(f"\tremoved")
            else:
                print(f"\tconcept {concept_to_remove} is not present in translations for string '{string}'")

            # if the resulting string translations list is empty, remove the string from translations list
            if len(self.concepts.get(string)) == 0:
                self.concepts.pop(string)
                print(f"\tstring {string} removed as well")
        return

    def removeMethodOfString(self, string, method_to_remove):
        """
        Remove string-method translation from container.
        If the translation was last for given string, the string gets removed from the translations as well.

        :param string: string that has the method assigned
        :param method_to_remove: method to be removed
        :return: None if the string was not in the containers string-method translations
                0 if the string translations was empty and the string was removed from the translations
                1 on successful removal of the method from container's list
        """

        if self.methods.get(string) is None:
            print(f"\tString '{string}' is not present in string-method translations of container {self.id}")

        else:
            remi = None
            print(f"removing method {method_to_remove} of string '{string}'")
            i = 0
            for methods_of_string in self.methods.get(string):
                # print(concepts_of_string)
                if methods_of_string["vocabulary"] == method_to_remove["vocabulary"] and methods_of_string["uri"] == method_to_remove["uri"]:
                    remi = i
                i += 1
            if remi is not None:
                del(self.methods.get(string)[remi])
                print(f"\tremoved")
            else:
                print(f"\tmethod {method_to_remove} is not present in translations for string '{string}'")

            # if the resulting string translations list is empty, remove the string from translations list
            if len(self.methods.get(string)) == 0:
                self.methods.pop(string)
                print(f"\tstring {string} removed as well")
        return

    def removeUnitOfString(self, string, unit_to_remove):
        """
        Remove string-unit translation from container.
        If the translation was last for given string, the string gets removed from the translations as well.

        :param string: string that has the unit assigned
        :param unit_to_remove: unit to be removed
        :return: None if the string was not in the containers string-unit translations
                0 if the string translations was empty and the string was removed from the translations
                1 on successful removal of the unit
        """

        if self.units.get(string) is None:
            print(f"\tString '{string}' is not present in string-unit translations of container {self.id}")

        else:
            remi = None
            print(f"removing unit {unit_to_remove} of string '{string}'")
            i = 0
            for units_of_string in self.units.get(string):
                # print(concepts_of_string)
                if units_of_string["vocabulary"] == unit_to_remove["vocabulary"] and units_of_string["uri"] == unit_to_remove["uri"]:
                    remi = i
                i += 1
            if remi is not None:
                del(self.units.get(string)[remi])
                print(f"\tremoved")
            else:
                print(f"\tunit {unit_to_remove} is not present in translations for string '{string}'")

            # if the resulting string translations list is empty, remove the string from translations list
            if len(self.units.get(string)) == 0:
                self.units.pop(string)
                print(f"\tstring {string} removed as well")
        return
    def removeAllConcepts(self):
        """
        Removes all string-concept assigned to container
        :return: None
        """
        self.concepts = {}
        return None

    def removeAllMethods(self):
        """
        Removes all string-method translation assigned to container
        :return: None
        """
        self.methods = {}
        return None

    def removeAllUnits(self):
        """
        Removes all string-unit translations assigned to container
        :return: None
        """
        self.units = {}
        return None

    def collectConcepts(self, collection={}, cascade=True):
        """
        Collects assigned string-concepts translations from the container and recursively from all sub-containers if desired

        :param collection: the collection of string-concepts translations that will be returned
        :param cascade: whether to include translations from sub-containers
        :return: collection of string-concepts translations {the string: [{'vocabulary': vocabulary string, 'uri': uri string}, {...}]
        """
        # collect string-concepts from the container itself
        if len(self.concepts) > 0:
            updateVocabulary(collection, self.concepts)

        # collect concepts from child containers if desired
        if cascade:
            # then collect string-concepts from child containers
            for cont in self.containers:
                cont.collectConcepts(collection, cascade)

        return collection


    def collectMethods(self, collection={}, cascade=True):
        """
        Collects assigned string-methods translations from the container and recursively from all sub-containers if desired

        :param collection: the collection of string-methods translations that will be returned
        :param cascade: whether to include translations from sub-containers
        :return: collection of string-methods translations {the string: [{'vocabulary': vocabulary string, 'uri': uri string}, {...}]
        """
        # collect string-concepts from the container itself
        if len(self.methods) > 0:
            updateVocabulary(collection, self.methods)

        # collect methods from child containers if desired
        if cascade:
            # then collect string-methods from child containers
            for cont in self.containers:
                cont.collectMethods(collection, cascade)

        return collection

    def collectUnits(self, collection={}, cascade=True):
        """
        Collects assigned string-units translations from the container and recursively from all sub-containers if desired

        :param collection: the collection of string-units translations that will be returned
        :param cascade: whether to include translations from sub-containers
        :return: collection of string-units translations {the string: [{'vocabulary': vocabulary string, 'uri': uri string}, {...}]
        """
        # collect string-units from the container itself
        if len(self.units) > 0:
            updateVocabulary(collection, self.units)

        # collect units from child containers if desired
        if cascade:
            # then collect string-units from child containers
            for cont in self.containers:
                cont.collectUnits(collection, cascade)

        return collection

    def deleteOwnFiles(self, failed = []):
        """
        Deletes container's own file (if exists) from locale storage.
        First induces deleting own files of sub-containers to prevent errors.

        :param failed: list of unsuccessful attempts and reason for that [undeleted file path, description of error]
        :return: the same list of undeleted files
        """
        # first delete sub-container's files (if any)
        for c in self.containers:
            c.deleteOwnFiles(failed)

        # and afterwards the container's file/directory itself
        # only some of the subclasses have local file data
        if hasattr(self, 'path'):
            if self.path is not None:
                try:
                    if os.path.isfile(self.path):
                        os.remove(self.path)
                    elif os.path.isdir(self.path):
                        os.rmdir(self.path)
                except FileNotFoundError:
                    failed.append([self.path, "file does not exist"])
                    # raise LocalFileManipulationError(f"Failed to delete '{self.path}'"
                    #                                  f" from local files storage - the file does not exist.")
                except PermissionError:
                    failed.append([self.path, "permission error"])
                    # raise LocalFileManipulationError(
                    #     f"Failed to delete '{self.path}' from local files storage - the file is locked by another process.")

        return failed

class PublisherFactory:
    """
    Publisher object factory
    """

    # directory of registered publisher types classes
    publishers = {}

    # the one and only instance
    _instance = None

    @classmethod
    def registerPublisher(cls, publisherClass):
        cls.publishers[publisherClass.key] = publisherClass
        print("Publisher '{}' registered".format(publisherClass.key))
        return

    @classmethod
    def createHandler(cls, publisherKey, *args):
        """
        Creates and returns instance of Publisher of given key
        """
        if publisherKey not in cls.publishers.keys():
            raise ValueError(
                "Unsupported publisher handler type '{}'.\nRegistred data publishers are: {}".format(publisherKey,
                                                                                                     ",".join(
                                                                                                         ["'" + k + "'"
                                                                                                          for k in
                                                                                                          cls.publishers.keys()])))
        elif publisherKey is None:
            raise ValueError("Publisher handler type can't be None")
        else:
            newPublisher = cls.publishers[publisherKey](*args)
            return newPublisher

    def __init__(self):

        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance



class Publisher():
    key = None
    name = None

    def __init__(self):
        # make the class properties accessible through instance properties
        self.key = type(self).key
        self.name = type(self).name

    def getFileInfo(self, *args):
        pass

    def getMetadata(self, *args):
        pass

class Pointer:
    """
    Points to an exact location in a resource and defines a way to extract the value of a particular metadata entity instance.
    Concrete implementations defined in subclasses.
    """
    pass

class ProjectPointer(Pointer):
    """
    Pointer that is not related to any provided file/table.
    For metadata elements that are found/created for the Project.
    """

    pass

class Datasetpointer(Pointer):
    """
    Pointer that is not related to any provided file/table.
    For metadata elements that are created for the Dataset.
    """

    pass

class CrawlerFactory:
    """
    Factory of Crawler class instances
    """

    # directory of registered publisher types classes
    crawlerTypes = {}
    crawlerExtensions = {}

    @classmethod
    def registerCrawlerType(cls, crawler_class):
        cls.crawlerTypes[crawler_class.crawlerType] = crawler_class
        print(f"> Crawler type '{crawler_class.crawlerType}' registered.")
        return

    @classmethod
    def createCrawler(cls, general_type, container, *args, **kwargs):
        """
        Creates and returns instance of Crawler subclass based on registered types and their specialization procedures
        """
        # if 'crawler_type' is in kwargs and is not None - e.a. loading the container from DB
        if kwargs.get("crawler_type") is not None:
            specialized_type = kwargs.pop("crawler_type")
            return cls.crawlerTypes[specialized_type](container, *args, **kwargs)

        # creating new crawler based on container properties
        else:
            if general_type is not None:
                if general_type not in cls.crawlerTypes.keys():
                    print(cls.crawlerTypes.keys())
                    types = ",".join(["'" + k + "'" for k in cls.crawlerTypes.keys()])
                    print(
                        f"\t{os.path.basename(container.path)} - unsupported Crawler subclass general type '{general_type}' (registered types are: {types}) - 'zero crawler' will be used instead.")

                    return cls.crawlerTypes['zero'](container, *args)
                else:
                    # get specialized crawler type
                    specialized_type = cls.crawlerTypes[general_type].getSpecializedCrawlerType(container, *args, **kwargs)
                    # check if the requested specialized crawler type is registered in the factory
                    if specialized_type not in CrawlerFactory.crawlerTypes.keys():
                        types = ",".join(["'" + k + "'" for k in cls.crawlerTypes.keys()])
                        print(f"\t{os.path.basename(container.path)} - unsupported Crawler subclass special type "
                              f"'{specialized_type}' (registered types are: {types}) - 'zero crawler' will be used instead.")

                        return cls.crawlerTypes['zero'](container, *args, **kwargs)
                    else:
                        # try if the specialized crawler is valid for given container
                        tryCrawler = cls.crawlerTypes[specialized_type](container, *args, **kwargs)
                        if tryCrawler.validate():
                            return tryCrawler
                        # or return the general type
                        else:
                            fallback_type = cls.crawlerTypes[general_type].getFallbackCrawlerType(container, *args, **kwargs)
                            return cls.crawlerTypes[fallback_type](*args, **kwargs)

            else:
                print(f"\tCrawler type was not specified - 'zero crawler' will be used instead.")
                return cls.crawlerTypes['zero'](container, *args)

    def __init__(self):
        pass

class Crawler:
    """
    Top level abstract class of the metadata/data crawler
    """
    crawlerType = 'zero'

    @classmethod
    def getSpecializedCrawlerType(cls, container, **kwargs):
        return cls.crawlerType
    @classmethod
    def getFallbackCrawlerType(cls, container, **kwargs):
        return cls.crawlerType

    def __init__(self, container):
        self.container = container
        pass

    def validate(self):
        """
        Validates suitability of particular crawler type for given container
        """
        return True

    def analyze(self):
        """
        Analyzes inner structure of the container
        :return: list of containers - container tree
        """

        print(f"No content analysis procedure defined for crawler type '{self.crawlerType}'")
        self.container.isAnalyzed = True
        return []

    def crawl(self):
        """
        Parses the container content and searches for meatadata elements.
        :return: MetadataStructureMap
        """
        print(f"No crawling procedure defined for crawler type '{self.crawlerType}'")

        return

CrawlerFactory.registerCrawlerType(Crawler)

def get_formated_file_size(path):
    """Return a string of dynamically formatted file size."""
    suffix = "B"
    if os.path.isfile(path):
        size = os.stat(path).st_size
    else:
        size = get_directory_size(path)
    if size:
        for unit in ("", "k", "M", "G", "T", "P", "E", "Z"):
            if abs(size) < 1024.0:
                return f"{size:3.1f} {unit}{suffix}"
            size /= 1024.0
        return f"{size:.1f}Yi{suffix}"
    else:
        return None

def get_directory_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if not os.path.islink(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def updateVocabulary(target_vocab, input_vocab):
    """
    General function to update one vocabulary (concepts/methods/units) by another.
    Strings from input vocabulary are added to target vocabulary if not there already.
    Translations from input vocabulary are added to target vocabulary if not there already
    """
    # iterate over each string in the input vocabulary
    for string, input_translations in input_vocab.items():
        # check if the string exists in the target vocabulary
        if string in target_vocab.keys():
            # get the list of translations for the string in the target vocab
            target_translations = target_vocab[string]
            # create a set of existing translation tuples (vocabulary, uri) in the target vocab
            existing_translations_set = set(
                (translation['vocabulary'], translation['uri']) for translation in target_translations
            )
            # iterate through each translation in the input vocab
            for input_translation in input_translations:
                translation_tuple = (input_translation['vocabulary'], input_translation['uri'])

                # if the translation doesn't already exist, add it to the target vocab
                if translation_tuple not in existing_translations_set:
                    target_translations.append(input_translation)
        else:
            # If the string does not exist in the target vocabulary, add it with its translations
            target_vocab.update({string: input_translations})
    return