# coding = utf-8
# -*- coding: utf-8 -*-

import requests
import os
import sys
import shutil
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
        # on initialization load Project from DB or establish a new one
        self.dbconnection = db_connection
        self.ownerID = user_id
        self.name = kwargs.get("name")

        self.doi = kwargs.get("doi")
        # list of Dataset class instances present within this project
        self.datasets = []
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
        # uploaded files directly from the users computer
        self.uploadedFiles = []
        # the tree structure of included files and other container types
        self.containerTree = []
        # dictionary of file paths and related container IDs - useful for cross-checking between files and containers
        self.containersOfPaths = {}
        # language of the project
        self.language = None

        # dedicated directory for file saving
        self.temp_dir = None
        # for now - some kind of licences definition and appropriate actions should be implemented
        self.keepFiles = False

        # project's own ContainerHandlerFactory to keep track of containers
        self.containerFactory = ContainerHandlerFactory()
        # the crawlers factory
        self.crawlerFactory = CrawlerFactory()

        if kwargs.get("id") is None:
            # Try to create a new project record in the database
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
            # Load the existing project properties from the database
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
        print(f"\nSaving project \"{self.name}\" with ID {self.id} ... ")

        self.dbconnection.updateProjectRecord(self, cascade)

        print(f" ... successful.")
        return

    def getContainersSerialization(self):
        cont_dict = {}
        for cont in self.containerTree:
            cont_dict.update({cont.id: cont.getSerializationDictionary()})
        # print(f"collected serialization dictionary of all projects containers:\n{cont_dict}")
        return cont_dict

    def loadDBrecord(self, cascade=True):

        return True

    def setDOI(self, doi):
        """
        Changes the DOI of a project with all appropriate actions
        - reads the registration agency and publisher response metadata and assigns them to the ProjectManager
        - check for files bound to the DOI record
        - download the files (unpack archives if necessary)
        - create container tree from files
        - remove old files if there were any

        """

        # if the __doi parameter already had some value
        if self.doi:
            # and the new value differs from the previous one
            if self.doi != doi:
                # remove the files that were downloaded from the DOI record before
                self.deleteAllProjectFiles()
                pass

        if doi is not None:
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
            self.publisher = self.getPublisher(self.DOImetadata)
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

    def getDOI(self):
        """
        Private attribute __doi getter
        """
        return self.doi


    def getAllFilesList(self):
        filesList = []
        for cont in self.containerTree:
            cont.listOwnFiles(filesList)
        return filesList

    def deleteAllProjectFiles(self):
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
        for f in self.downloadedFiles:
            if os.path.isfile(f):
                try:
                    os.remove(f)
                except PermissionError as e:
                    failed.append(f)
                    print(f)
            if os.path.isdir(f):
                try:
                    os.rmdir(f)
                except PermissionError as e:
                    failed.append(f)
                    print(f)
        if len(failed) > 0:
            flist = "\n".join([f for f in failed])
            raise LocalFileManipulationError(f"Failed to delete following files:\n{flist}")
        else:
            print("All downloaded files successfully deleted.")
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
                    raise DOIdataRetrievalException(f"Provided DOI '{doi}' is invalid.")
                if RAjson[0]['status'] == "DOI does not exist":
                    raise DOIdataRetrievalException(f"Provided DOI '{doi}' is not registered.")
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
                print("downloading remote files to local storage ...")

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
        handles all needed steps to upload files from a session (unpack archives if necessary) and create file structure tree
        """

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
        return self.getContainerByID(pid).containers

    def newDataset(self, name):
        """
        Adds DatasetHandler instance to dataset list
        """
        new_dataset = Dataset(name, self)
        self.datasets.append(new_dataset)
        return new_dataset

    def addDataset(self, dataset):
        """
        Adds DatasetHandler instance to dataset list
        """
        self.datasets.append(dataset)
        return

    def removeDataset(self, item):
        """
        Removes DatasetHandler instance from dataset list
        """
        del self.datasets[item]
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


    def showDatasetsContents(self):
        for ds in self.datasets:
            ds.showContents()
        return

    def showFilesStructure(self):
        print("\n" + 80 * "-")
        print(f"{self.name}\nfile paths and related container IDs:")
        print(80 * "-")
        for path, contID in self.containersOfPaths.items():
            print(f"{path}\t[{contID}]")

class Dataset:
    """
    Represents a set of data containers that form together a distinct collection of data represented by a MetadataStructureMap.
    The instance has its own MetadataStructureMap that is being composed during the metadata generation phase
    """

    def __init__(self, name, project):
        # dataset name
        self.name = name
        # project reference
        self.project = project
        # data containers that the dataset consists of
        self.containers = []
        # the instance of the metadata mapping
        self.metadataMap = MetadataStructureMap()


    def addContainers(self, containers):
        """
        Adds one or more ContainerHandler instances to Dataset's containers list
        """
        if isinstance(containers, list):
            self.containers.extend(containers)
        else:
            self.containers.append(containers)
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
        print(f"\n==== {self.name} " + 70 * "=")

        if show_containers:
            self.showContainerTree()
        print(80 * "=" + 2 * "\n")

    def showContainerTree(self):
        """
        Induces printing contents of the whole container tree
        """
        print(f"---- container tree: ----")
        for container in self.containers:
            container.showContents(0)



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

        # dictionary of assigned concept URIs {"vocabulary": vocabulary provider, "uri": URI of the concept}
        self.concepts = kwargs.get("concepts") if kwargs.get("concepts") is not None else {}

    def __str__(self):
        out = f"\n|  # {self.id}  |  {type(self).__name__}\n|  {self.name}  |  parent: "
        out += f"{self.parentContainer.id}\n" if self.parentContainer is not None else f"project\n"
        if hasattr(self, "path"):
            out += f"|  {self.path}"
        return out


    def showContents(self, depth = 0, ind = ". "):
        """
        Prints structured info about the container and invokes showContents on all of its containers

        :param depth: current depth of showContent recursion
        :param ind: string of a single level indentation
        """
        # get the indentation string
        t = ind * depth
        # print attributes of this container
        pContID = self.parentContainer.id if self.parentContainer is not None else "root"
        # print(f"{t}{self.id} - {self.name} ({self.containerType}) [{len(self.containers)}] {'{'+self.crawler.crawlerType+'}'}  >{pContID}")
        print(f"{t}{self.id} - {self.name} ({self.containerType}) [{len(self.containers)}] >{pContID}")

        # invoke showContents of sub-containers
        if len(self.containers) > 0:
            depth += 1
            for cont in self.containers:
                cont.showContents(depth)

    def updateDBrecord(self, db_connection, cascade=True):
        db_connection.updateContainerRecord(self, cascade)
        return

    def getSerializationDictionary(self, cascade=True):
        # general properties of all containers
        dict = {"id": self.id,
                "type": self.containerType,
                "name": self.name,
                "parent_id_local": self.parentContainer.id if self.parentContainer is not None else None,
                "crawler_type": self.crawler.crawlerType if self.crawler is not None else None}

        # type-specific properties
        for key, attr_name in self.serializationDict.items():
            dict.update({key: str(getattr(self, attr_name))})

        # and recursion for the sub-containers
        if cascade:
            sub_conts = {}
            for cont in self.containers:
                sub_conts.update({cont.id: cont.getSerializationDictionary()})
            dict.update({"containers": sub_conts})
        return dict

    def collectContainerIDsToList(self, output=[]):
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

    def deleteOwnFiles(self, failed = []):
        """
        Deletes container's own file (if exists) from locale storage and induces deleting own files of subcontainers

        :param failed: list of unsuccessful attemtps and reason for that [undeleted file path, description of error]
        :return: the same list of undeleted files
        """
        # first delete sub-container's files (if any)
        for c in self.containers:
            c.deleteOwnFiles(failed)
        # only some of the subclasses have local file data
        if hasattr(self, 'path'):
            if self.path is not None:
                try:
                    # and afterwards the container's file/directory itself
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

