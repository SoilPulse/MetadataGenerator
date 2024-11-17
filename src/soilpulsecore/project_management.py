# coding = utf-8
# -*- coding: utf-8 -*-

import requests
import os
import sys
import shutil
import json
from pathlib import Path
from frictionless import Package, Resource
import re

from .metadata_scheme import MetadataStructureMap
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

        # project concepts translations dictionary
        self.conceptsTranslations = {}
        # project methods translations dictionary
        self.methodsTranslations = {}
        # project units translations dictionary
        self.unitsTranslations = {}

        # get global vocabularies from DBconnector
        self.globalConceptsVocabularies = self.dbconnection.concepts_vocabularies
        self.globalMethodsVocabularies = self.dbconnection.methods_vocabularies
        self.globalUnitsVocabularies = self.dbconnection.units_vocabularies

        # dedicated directory for file saving
        self.temp_dir = None
        # dedicated subdirectory for datasets files
        self.datasets_dir = None
        # for now - some kind of licences definition and appropriate actions should be implemented
        self.keepFiles = False

        # project's own ContainerHandlerFactory to keep track of containers
        self.containerFactory = ContainerHandlerFactory(self)
        # the crawlers factory
        self.crawlerFactory = CrawlerFactory()

        # list of Dataset class instances existing within this project
        self.datasets = []

        # if ID is None establish a new project on the storage
        if kwargs.get("id") is None:
            try:
                self.id, self.temp_dir, self.datasets_dir = self.dbconnection.establishProjectRecord(user_id, self)
            except DatabaseEntryError as e:
                print("Failed to establish new Project record in SoilPulse database.")
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
        - remove old files if there were any
        :param doi: DOI to apply
        """
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
            if self.registrationAgency is not None:
                # populate the metadata properties
                self.DOImetadata = self.getDOImetadata(doi)
                if self.DOImetadata:
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
                        self.publisherMetadata = self.publisher.getMetadata()

                        # append the publisher metadata JSON container to the ProjectManagers containers
                        publisherCont = self.containerFactory.createHandler("json", name=publisher_metadata_key, project_manager=self, parent_container=None, content=self.publisherMetadata, path=None)
                        self.containerTree.append(publisherCont)
                        publisherCont.saveAsFile(self.temp_dir, publisher_metadata_key.replace(" ", "_")+".json")

                        # get downloadable files information from publisher
                        self.publishedFiles = self.publisher.getFileInfo()
                else:
                    print("DOI metadata were not retrieved.")
            else:
                print("DOI metadata were not retrieved.")
        else:
            print("Empty DOI provided. DOI metadata were not retrieved.")
        return

    def getAllFilesList(self):
        """
        Collects file paths from all containers in the tree
        :return: list of file paths
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
        """
        Deletes all files that are stored in the list of downloaded files
        """
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
        """
        Deletes all files that are stored in the list of uploaded files
        """
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
        Gets the Publisher class instance from what's stored in the DOI metadata
        """
        if not DOI_metadata:
            try:
                DOImetadata = self.getDOImetadata(self.doi)
            except DOIdataRetrievalException as e:
                print("Error occurred while retrieving DOI record metadata.")
                print(e.message)
                return None
        else:
            try:
                publisherKey = DOI_metadata['data']['attributes']['publisher']
            except AttributeError as e:
                print("Couldn't find publisher value in the DOI registration agency metadata response.")
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
                return None
            except requests.exceptions.Timeout:
                print(" The request timed out.")
                return None
            except requests.exceptions.HTTPError as e:
                print(" HTTP Error:", e)
                return None
            except requests.exceptions.RequestException as e:
                print(" An error occurred:", e)
                return None
            else:
                if 'error' in output.keys():
                    raise DOIdataRetrievalException(f"Registration agency '{ProjectManager.getRegistrationAgencyOfDOI(doi)}' didn't respond. Error {output['status']}: {output['error']}")
                print(" ... successful\n")
                return output
        else:
            print("Unsupported registration agency '{}'".format(RA))
            raise DOIdataRetrievalException(f"Unsupported registration agency '{RA}'")

    def downloadPublishedFiles(self, list = None):
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
                            print(f"\tThe request timed out while trying to download file from URL:\n'{url}'")
                            return False
                        except requests.exceptions.HTTPError as e:
                            print(f"\tHTTP Error occurred while trying to download file from URL:\n'{url}'\n", e)
                            return False
                        except requests.exceptions.RequestException as e:
                            print(f"\tRequest Error occurred while trying to download file from URL:\n'{url}'\n", e)
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
        :param files: path string or list of path strings
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
            newContainer.getAnalyzed(cascade=True)
            self.containerTree.append(newContainer)
            # add new file path to uploaded files list
            self.uploadedFiles.append(newContainer.path)
        return

    def downloadFilesFromURL(self, urls):
        """
        Handles all needed steps to download file/files from a session (unpack archives if necessary) and create file structure tree
        :param urls: url string or list of url strings
        """
        from urllib.parse import urlparse, unquote

        if not isinstance(urls, list):
            urls = [urls]

        fileList = []
        for url in urls:
            filename = unquote(urlparse(url).path.split("/")[-1])
            local_path = os.path.join(self.temp_dir, filename)
            # print(f"{filename} -> {local_path}")
            try:
                response = requests.get(url)
            except requests.exceptions.ConnectionError:
                print(
                    "\tA connection error occurred while trying to download file from URL - check your internet connection.")
                return False
            except requests.exceptions.Timeout:
                print(f"\tThe request timed out while trying to download file from URL:\n'{url}'")
                return False
            except requests.exceptions.HTTPError as e:
                print(f"\tHTTP Error occurred while trying to download file from URL:\n'{url}'\n", e)
                return False
            except requests.exceptions.RequestException as e:
                print(f"\tRequest Error occurred while trying to download file from URL:\n'{url}'\n", e)
                return False
            else:
                if response.ok:
                    with open(local_path, mode="wb") as filesave:
                        filesave.write(response.content)

                    # create new container from the file with all related actions
                    newContainer = self.containerFactory.createHandler('filesystem', self, None,
                                                                       name=filename, path=local_path)
                    self.containerTree.append(newContainer)

                else:
                    # something needs to be done if the response is not OK ...
                    print("\t\tThe response was not OK!")

                    return False

        print(" ... successful\n")
        self.downloadedFiles.extend(fileList)
        return fileList


    def getContainerByID(self, cid):
        """
        Returns container instances  of given ID/IDs
        :param cid: single ID or a list of IDs
        """
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

    def removeContainer(self, container):
        # first remove sub-containers if any
        for sub_cont in container.containers:
            print(f"\tremoving container {sub_cont.id}")

            # self.removeContainer(cont)
            self.removeContainer(sub_cont)

        self.containerFactory.removeContainerByID(container.id)
        # remove the container itself from project instance
        # for i, cont in enumerate(self.containerTree):
        #     if cont.id == container.id:
        #         del self.containerTree[i]
        #         break

        # remove the link to dataset

        return

    def createDataset(self, name, id=None):
        """
        Adds Dataset object instance to dataset list, creates directory in project datasets folder
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
        # create dedicated directory for the dataset
        new_dataset.createDedicatedDirectory()
        # append the dataset to the list of the project
        self.datasets.append(new_dataset)

        return new_dataset

    def removeDataset(self, dataset):
        """
        Removes Dataset object instance from project's datasets.
        Deletes dataset's directory.

        :param dataset: Dataset handler object instance
        """

        # find index of the dataset in projects datasets
        index = None
        i = 0
        for ds in self.datasets:
            if ds.id == dataset.id:
                index = i
                # break the loop when found
                break
            i += 1

        if index is None:
            print(f"Specified dataset {dataset.id} - {dataset.name} can't be removed because it was not found in project {self.id}.")
        else:
            self.removeDatasetByIndex(index)
        return

    def removeDatasetByIndex(self, index):
        """
        Removes Dataset object instance from dataset list by index.
        Deletes dataset's directory

        :param index: index of the dataset in the self.datasets list
        """
        try:
            dataset = self.datasets[index]
        except IndexError:
            print(f"Can't remove dataset by index {index} because the project currently contains only {len(self.datasets)} items.")
        else:
            # remove record from DB
            self.dbconnection.deleteDatasetRecord(dataset)
            # remove dataset from the list
            del self.datasets[index]

            print(f"dataset #{dataset.id} - '{dataset.name}' was deleted from project")
            # remove also all dataset's file
            if dataset.directory_path is not None:
                if os.path.isdir(dataset.directory_path):
                    shutil.rmtree(dataset.directory_path)
        return

    def removeDatasetByID(self, dataset_id):
        """
        Removes Dataset object instance from project's datasets based on its ID.
        Deletes dataset's directory.

        :param dataset_id: Local (project scope) Dataset ID to be removed
        """

        # find index of the dataset in projects datasets
        index = None
        i = 0
        for ds in self.datasets:
            if ds.id == dataset_id:
                index = i
                # break the loop when found
                break
            i += 1

        if index is None:
            print(
                f"Dataset with ID {dataset_id} can't be removed because it was not found in project {self.id}.")
        else:
            self.removeDatasetByIndex(index)
        return

    def removeAllDatasets(self):
        """
        Removes all datasets from a project including all their directories
        """
        for ds in self.datasets:
            self.removeDataset(ds)

    def showContainerTree(self, show_concepts=True, show_methods=True, show_units=True):
        """
        Induces printing contents of the whole container tree
        """
        print("\n" + 80 * "=")
        print(f"{self.name}\ncontainer tree:")
        print(80 * "-")
        for container in self.containerTree:
            container.showContents(show_concepts=show_concepts, show_methods=show_methods, show_units=show_units)
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
                updateTranslationsDictionary(project_concepts, all_containers_concepts)
        return project_concepts

    def collectAllMethods(self):
        """
        Collects all methods from containers of the tree
        """
        project_methods = {}
        for cont in self.containerTree:
            all_containers_methods = cont.collectMethods({}, True)
            if len(all_containers_methods) > 0:
                updateTranslationsDictionary(project_methods, all_containers_methods)
        return project_methods

    def collectAllUnits(self):
        """
        Collects all units from containers of the tree
        """
        project_units = {}
        for cont in self.containerTree:
            all_containers_units = cont.collectUnits({}, True)
            if len(all_containers_units) > 0:
                updateTranslationsDictionary(project_units, all_containers_units)
        return project_units

    def updateConceptsTranslationsFromContents(self):
        """
        Updates project's string-concept translations by translations from own containers
        """
        concepts_of_containers = self.collectAllConcepts()
        updateTranslationsDictionary(self.conceptsTranslations, concepts_of_containers)
        return

    def updateMethodsTranslationsFromContents(self):
        """
        Updates project's string-method translations by translations from own containers
        """
        methods_of_containers = self.collectAllMethods()
        updateTranslationsDictionary(self.methodsTranslations, methods_of_containers)
        return

    def updateUnitsTranslationsFromContents(self):
        """
        Updates project's string-unit translations by translations from own containers
        """
        units_of_containers = self.collectAllUnits()
        updateTranslationsDictionary(self.unitsTranslations, units_of_containers)
        return
    def updateConceptsTranslationsFromFile(self, input_file):
        """
        Adds string-concepts translations to project's dictionary (if not already there) from specified file
        :param input_file: path of a file to load
        """
        # load the input JSON file to dictionary
        str_conc_dict = self.loadTranslationsFromFile(input_file)
        updateTranslationsDictionary(self.conceptsTranslations, str_conc_dict)
        return

    def updateMethodsTranslationsFromFile(self, input_file):
        """
        Adds string-method translations to project's dictionary (if not already there) from specified file
        :param input_file: path of a file to load
        """
        # load the input JSON file to dictionary
        str_meth_dict = self.loadTranslationsFromFile(input_file)
        updateTranslationsDictionary(self.methodsTranslations, str_meth_dict)
        return

    def updateUnitsTranslationsFromFile(self, input_file):
        """
        Adds string-concepts translations to project's dictionary (if not already there) from specified file
        :param input_file: path of a file to load
        """
        # load the input JSON file to dictionary
        str_unit_dict = self.loadTranslationsFromFile(input_file)
        updateTranslationsDictionary(self.unitsTranslations, str_unit_dict)
        return


    def loadTranslationsFromFile(self, input_file):
        """
        Loads string-* translations JSON file

        :param input_file: path of vocabulary file to load from
        """

        # load the input JSON file
        str_dict = {}
        with open(input_file, 'r') as f:
            try:
                for str in json.load(f):
                    str_dict.update({str['string']: str["translation"]})
            except KeyError as e:
                print(f"Translations dictionary '{input_file}' failed to load.")
        return str_dict

    def exportTranslationsDictionaryToFile(self, dictionary, filepath):
        """
        Saves string translations dictionary to a file, overwrites if exists
        :param dictionary: dictionary to dump
        :param filepath: path of a file to save
        """
        with open(filepath, "w") as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=4)

    def showDictionaries(self):
        """
        Prints structured dictionaries contents to console
        """
        print(f"\nString-concept translations dictionary of project '{self.name}'{' is empty.' if len(self.conceptsTranslations) == 0 else ':'}")
        if len(self.conceptsTranslations) > 0:
            for string, concepts in self.conceptsTranslations.items():
                print(f"\t\"{string}\"")
                for concept in concepts:
                    print(f"\t\t{concept}")

        print(f"\nString-method translations dictionary of project '{self.name}'{' is empty.' if len(self.methodsTranslations) == 0 else ':'}")
        if len(self.methodsTranslations) > 0:
            for string, methods in self.methodsTranslations.items():
                print(f"\t\"{string}\"")
                for method in methods:
                    print(f"\t\t{method}")

        print(f"\nString-unit translations dictionary of project '{self.name}'{' is empty.' if len(self.unitsTranslations) == 0 else ':'}")
        if len(self.unitsTranslations) > 0:
            for string, units in self.unitsTranslations.items():
                print(f"\t\"{string}\"")
                for unit in units:
                    print(f"\t\t{unit}")
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
        # container object instances that are members of the dataset
        self.containers = []
        # directory to store files
        self.directory_path = None
        # the instance of the metadata mapping
        self.metadata_map = MetadataStructureMap()
        # transformation steps for the frictionless package
        self.steps = []

    def get_frictionless_package(self, output_path=None):
        """
        Composes frictionless package from containers of the dataset.
        Recursively searches for table containers and then builds valid Package instance
        :param output_path: file path to save the package descriptor
        """
        def collect_tables(cont_list, tables=[]):
            for cont in cont_list:
                if hasattr(cont, "fl_resource"):
                   if cont.fl_resource is not None:
                        tables.append(cont.get_frictionless_resource())
                if len(cont.containers) > 0:
                    collect_tables(cont.containers, tables=tables)
            return tables

        table_resources = collect_tables(self.containers)
        package = Package(resources=table_resources)

        if output_path:
            package.to_json(output_path)  # Save as JSON
        return package

    def load_transformation_steps(self, path):
        """
        Loads a file content and tries to evaluate it as a steps definition for transformation Pipeline
        """
        with open(path, 'r') as f:
            self.steps = eval(f.read())
        print(f"loaded transformation steps for dataset #{self.id} - '{self.name}':\n {self.steps}")
        return

    def createDedicatedDirectory(self):
        """
        Creates directory for a dataset to store its files
        """
        path = os.path.join(self.project.temp_dir, self.project.datasets_dir, str(self.id))
        if not os.path.isdir(path):
            os.mkdir(path)
        self.directory_path = path
        return path

    def addContainers(self, containers):
        """
        Wrapper for adding more containers at once in a list to Dataset's containers list
        """
        if isinstance(containers, list):
            for cont in containers:
                self.addContainer(cont)
        else:
            self.addContainer(containers)
        return

    def addContainer(self, container):
        """
        Adds a ContainerHandler instances to Dataset's containers list
        """
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
        """
        Invokes saving/updating of the dataset storage record
        """
        print(f"\tupdating dataset '{self.name}' ... ")
        db_connection.updateDatasetRecord(self)
        return

    def getContainerIDsList(self):
        """
        Return list of container IDs that are directly in the dataset
        """
        return [c.id for c in self.containers]

    def getAllContainerIDsList(self):
        """
        Return list of IDs of all containers that belong to dataset
        (all containers within containers)
        """
        def collect_ids(cont_list, ids=[]):
            for cont in cont_list:
                ids.append(cont.id)
                if len(cont.containers) > 0:
                    collect_ids(cont.containers, ids=ids)
            return ids

        return collect_ids(self.containers)


    def showContents(self, show_containers=True, show_concepts=True, show_methods=True, show_units=True):
        print(f"\n==== {self.name} " + 60 * "=" + f" #{self.id}")

        if show_containers:
            self.showContainerTree(show_concepts, show_methods, show_units)
        print(80 * "=" + "\n")

    def showContainerTree(self, show_concepts=True, show_methods=True, show_units=True):
        """
        Induces printing contents of the dataset's container tree
        """
        print(f"---- container tree: ----")
        for container in self.containers:
            container.showContents(0, show_concepts=show_concepts, show_methods=show_methods, show_units=show_units)

    def getSerializationDictionary(self):
        return {"id": self.id, "name": self.name, "container IDs": [c.id for c in self.containers]}


    def getFrictionlessCompleteTransformation(self):

        return

    def checkMetadataStructure(self):
        self.metadataMap.checkConsistency()

    def getAnalyzed(self, cascade=True, force=False, report=False):
        """Induces analysis of own containers."""
        for container in self.containers:
            container.getAnalyzed(cascade, force, report)
        pass

    def getCrawled(self, cascade=True, force=False, report=False):
        """Induces crawling of own containers"""
        for container in self.containers:
            container.getCrawled(cascade, force, report)

    def removeAllConcepts(self):
        """
        Removes all concepts from all containers within dataset
        """
        for container in self.containers:
            container.removeAllConcepts(cascade=True)

    def removeAllMethods(self):
        """
        Removes all methods from all containers within dataset
        """
        for container in self.containers:
            container.removeAllMethods(cascade=True)

    def removeAllUnits(self):
        """
        Removes all units from all containers within dataset
        """
        for container in self.containers:
            container.removeAllUnits(cascade=True)

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
        """
        Returns list of needed fields for storing all container types that are registered in factory
        """
        needed_fields = []
        for key, typeClass in cls.containerTypes.items():
            for fieldname in typeClass.DBfields.keys():
                needed_fields.append(fieldname)
        return needed_fields

    def __init__(self, project):

        # the project instance the factory belongs to
        self.project = project
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
            # print(f"type of weakref object: {type(weakref.ref(new_container))}")
            # return weakref.ref(new_container)
            return new_container

    def getContainerByID(cls, cid):
        """
        Returns container of given ID from inner dictionary
        """

        if cls.containers.get(cid) is not None:
            return cls.containers.get(cid)
        else:
            raise ContainerStructureError(
                f"Container id = {cid} was never created by this factory or was already removed.")

    def removeContainerByID(self, cid):
        """
        Removes container with given local ID and all of its sub-containers from projects container tree
        """

        if cid in self.containers.keys():
            print(f"deleting container {cid}")
            del(self.containers[cid])
        else:
            raise ContainerStructureError(
                f"Container id = {cid} was never created by this factory or was already removed.")
        pass

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
        self.wasAnalyzed = False

        # dictionary of string-concept translations {the string: [{"vocabulary": vocabulary provider, "uri": URI of the concept}, ...]
        self.concepts = kwargs.get("concepts") or {}
        # dictionary of string-method translations {the string: [{"vocabulary": vocabulary provider, "uri": URI of the method}, ...]
        self.methods = kwargs.get("methods") or {}
        # dictionary of string-unit translations {the string: [{"vocabulary": vocabulary provider, "uri": URI of the unit}, ...]
        self.units = kwargs.get("units") or {}

    def __str__(self):
        out = f"\n|  # {self.id}  |  name: '{self.name}'  |  parent: "
        out += f"{self.parentContainer.id}\n" if self.parentContainer is not None else f"project root\n"
        out += f"|  class: {type(self).__name__}"
        out += f"|  crawler class: {type(self.crawler).__name__}\n" if self.crawler else "\n"
        if hasattr(self, "path"):
            out += f"|  {self.path}\n"
        if hasattr(self, "concepts"):
            out += f"|  string-concept translations: {'-' if len(self.concepts) == 0 else ''}"
            for string, concs in self.concepts.items():
                out += f"|\t\"{string}\""
                for conc in concs:
                    out += f"|\t\t{conc}"
            out += "\n"
        if hasattr(self, "methods"):
            out += f"|  string-method translations: {'-' if len(self.methods) == 0 else ''}"
            for string, meths in self.methods.items():
                out += f"|\t\"{string}\""
                for meth in meths:
                    out += f"|\t\t{meth}"
            out += "\n"
        if hasattr(self, "units"):
            out += f"|  string-unit translations: {'-' if len(self.units) == 0 else ''}"
            for string, units in self.units.items():
                out += f"|\t\"{string}\""
                for unit in units:
                    out += f"|\t\t{unit}"
            out += "\n"
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
        crawler = ' - '+self.crawler.crawlerType if self.crawler.crawlerType == self.containerType else ''
        print(f"{t}{self.id} - {self.name} ({self.containerType}{crawler}) [{len(self.containers)}] ^{pContID}")
        if show_concepts:
            if hasattr(self, "concepts"):
                print("  " * (depth + 1) + "concepts:") if len(self.concepts) > 0 else None
                for string, concepts in self.concepts.items():
                    add = "  " * (depth + 2) + string + ": "
                    i = 0
                    for conc in concepts:
                        if i > 0:
                            add += "; "
                        if conc.get('term'):
                            add += f"'{conc['term']}' "
                        if conc.get('locator'):
                            add += f"[{conc['locator']['start_char']}:{conc['locator']['end_char']}] "
                        add += f"{conc['uri']} ({conc['vocabulary']})"
                        i += 1
                    print(add)

        if show_methods:
            if hasattr(self, "methods"):
                print("  " * (depth + 1) + "methods:") if len(self.methods) > 0 else None
                for string, methods in self.methods.items():
                    add = "  " * (depth + 2) + string + ": "
                    i = 0
                    for meth in methods:
                        if i > 0:
                            add += "; "
                        if meth.get('term'):
                            add += f"'{meth['term']}' "
                        if meth.get('locator'):
                            add += f"[{meth['locator']['start_char']}:{meth['locator']['end_char']}] "
                        add += f"{meth['uri']} ({meth['vocabulary']})"
                        i += 1
                    print(add)
        if show_units:
            if hasattr(self, "units"):
                print("  " * (depth + 1) + "units:") if len(self.units) > 0 else None
                for string, units in self.units.items():
                    add = "  " * (depth + 2) + string + ": "
                    i = 0
                    for unit in units:
                        if i > 0:
                            add += "; "
                        if unit.get('term'):
                            add += f"'{unit['term']}' "
                        if unit.get('locator'):
                            add += f"[{unit['locator']['start_char']}:{unit['locator']['end_char']}] "
                        add += f"{unit['uri']} ({unit['vocabulary']})"
                        i += 1
                    print(add)

        # invoke showContents of sub-containers
        if len(self.containers) > 0:
            depth += 1
            for cont in self.containers:
                cont.showContents(depth, ind, show_concepts, show_methods, show_units)

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

    def getAnalyzed(self, cascade=True, force=False, report=False):
        """
        Induces further decomposition of the container into logical sub-elements.
        """
        if self.wasAnalyzed and not force:
            print(f"Container {self.id} was already analyzed.")
            return False
        else:
            return  True

    def getCrawled(self, cascade=True, force=False, report=False):
        """
        Induces content search for metadata elements based on appropriate set of search rules and terms.
        """
        if self.wasCrawled and not force:
            print(f"Container {self.id} was already crawled.")
            return False
        else:
            return True

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
        # print(f"adding method {method} of string '{string}'")
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
    def removeAllConcepts(self, cascade=False):
        """
        Removes all string-concept assigned to container and all sub-containers recursively if desired
        :return: None
        """
        self.concepts = {}
        # cascade through if desired
        if cascade:
            for sub_cont in self.containers:
                sub_cont.removeAllConcepts(cascade)
        return None

    def removeAllMethods(self, cascade=False):
        """
        Removes all string-method translation assigned to container and all sub-containers recursively if desired
        :return: None
        """
        self.methods = {}
        # cascade through if desired
        if cascade:
            for sub_cont in self.containers:
                sub_cont.removeAllMethods(cascade)
        return None

    def removeAllUnits(self, cascade=False):
        """
        Removes all string-unit translations assigned to container and all sub-containers recursively if desired
        :return: None
        """
        self.units = {}
        # cascade through if desired
        if cascade:
            for sub_cont in self.containers:
                sub_cont.removeAllUnits(cascade)
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
            updateTranslationsDictionary(collection, self.concepts)

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
            updateTranslationsDictionary(collection, self.methods)

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
            updateTranslationsDictionary(collection, self.units)

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
            publi = ",".join(["'" + k + "'" for k in cls.publishers.keys()])
            raise ValueError(f"Unsupported publisher handler type '{publisherKey}'.\nRegistred data publishers are: {publi}")
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
        if kwargs.get("crawler_type"):
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

    def analyze(self, report=False):
        """
        Analyzes inner structure of the container
        :return: list of containers - container tree
        """

        print(f"No content analysis procedure defined for crawler type '{self.crawlerType}'")
        self.container.wasAnalyzed = True
        return []

    def crawl(self, report=False):
        """
        Parses the container content and searches for metadata elements.
        :return:
        """
        print(f"No crawling procedure defined for crawler type '{self.crawlerType}'")
        self.container.wasCrawled = True
        return

    def find_translations_in_dictionary(self, dictionary, min_match_length=2, full_match_only=True):
        """
        Searches for string matches between selected attributes of crawler's container and strings in dictionary.
        :param dictionary: the dictionary with string translations
        :param min_match_length: minimum length of a match to be included in results
        :param full_match_only: returns only perfect matches if True
        :return: list of matches
        """
        results = []
        # search in container name
        container_name = self.container.name.lower()
        # iterate over each term in the vocabulary to find matches in container name
        for str, translations in dictionary.items():
            str_pattern = re.compile(re.escape(str.lower()))
            matches = str_pattern.finditer(container_name)
            found_translations = []
            for match in matches:
                start_index = match.start()
                end_index = match.end() - 1
                match_length = match.end() - match.start()
                if full_match_only:
                    if match_length == len(container_name):
                        found_translations.extend(translations)
                # or filter out matches shorter than X characters
                elif match_length > min_match_length:
                    locator = {
                        "attribute": "name",
                        "start_char": start_index,
                        "end_char": end_index,
                    }

                    found_translations.extend(translations)
            results.append({container_name: found_translations}) if len(found_translations) > 0 else None

        # here could be some other searching ... whatever it may be

        return results

    def find_translations_in_vocabulary(self, vocabulary, min_match_length=3, full_match_only=False):
        """
        Searches for string matches between selected attributes of crawler's container and a term in vocabulary.
        :param vocabulary: the vocabulary with term meanings
        :param min_match_length: minimum length of a match to be included in results
        :param full_match_only: returns only perfect matches if True
        :return: list of matches
        """
        results = []
        # search in container name
        container_name = self.container.name.lower().strip(" _-")
        # iterate over each term in the vocabulary to find matches in container name
        for term in vocabulary:
            term_pattern = re.compile(re.escape(term["term"].lower().strip(" _-")))
            matches = term_pattern.finditer(container_name)
            found_translations = []
            for match in matches:
                start_index = match.start()
                end_index = match.end() - 1
                match_length = match.end() - match.start()
                if full_match_only:
                    if match_length == len(container_name):
                        found_translations.append(term)
                # or filter out matches shorter than X characters
                elif match_length > min_match_length:
                    locator = {
                        "attribute": "name",
                        "start_char": start_index,
                        "end_char": end_index,
                    }
                    # if the translation already contains "term"
                    term.update({"locator": locator})
                    found_translations.append(term)
            results.append({container_name: found_translations}) if len(found_translations) > 0 else None

        # here could be some other searching ... whatever it may be

        return results

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
    """
    Calculates total occupied space of a directory and its contents
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if not os.path.islink(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def updateTranslationsDictionary(target_vocab, input_vocab):
    """
    General function to update one translations dictionary (concepts/methods/units) by another.
    Strings from input dictionary are added to target dictionary if not there already.
    Translations from input dictionary are added to target vocabulary if not there already
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