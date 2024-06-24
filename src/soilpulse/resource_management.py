# coding = utf-8
# -*- coding: utf-8 -*-

import requests
import os
import shutil

from .metadata_scheme import MetadataStructureMap
from .db_access import DBconnector
from .exceptions import DOIdataRetrievalException, LocalFileManipulationError, ContainerStructureError, DatabaseEntryError

# general variables
downloadedFilesDir = "downloaded_files"
class ResourceManager:
    """
    Takes care of all files related to a resource composition.

    Singleton for a running session (only one ResourceManager can be edited and managed at a time)
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(ResourceManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, user_id, name = None, doi = None, id = None):
        # on initialization load Resource from DB or establish a new one
        if not hasattr(self, 'initialized'):  # Ensures __init__ is only called once
            self.dbconnection = DBconnector()
            self.ownerID = user_id

            if id is None:
                # Create a new resource record in the database
                try:
                    self.id = self.dbconnection.saveResourceManager(user_id, name, doi)
                except DatabaseEntryError as e:
                    print("Failed to establish new ResourceManager record in the SoilPulse database.")
                    raise

            else:
                # Load the existing resource from the database
                self.id = id
                self.dbconnection.loadResourceManager(id)

            # dedicated directory where files can be stored
            self.tempDir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), downloadedFilesDir,
                                        str(self.id))
            self.initialized = True

        # arbitrary resource name for easy identification
        self.name = name

        # list of Dataset class instances present within this resource
        self.datasets = []

        # registration agency of the DOI
        self.registrationAgency = None
        # metadata package from DOI record
        self.DOImetadata = None
        # publisher instance
        self.publisher = None
        # list of files that were published with the resource - publicly available through url
        self.publishedFiles = []
        # uploaded files directly from the users computer
        self.uploadedFiles = []
        # the tree structure of included files and other container types
        self.containerTree = []
        # the DOI is private, so it can't be changed without consequences - only setDOI(doi) can be used
        self.__doi = None

        # language of the resource
        self.language = None

        # for now - some kind of licences definition and appropriate actions should be implemented
        self.keepFiles = False

        if doi:
            self.setDOI(doi)


    def __del__(self):
        if hasattr(self, "keepFiles"):
            if not self.keepFiles:
                print(f"\n\nDeleting Resource's files because we can't keep them :-(")
                failed = self.deleteAllResourceFiles()
                if len(failed) > 0:
                    print(f"following files couldn't be deleted:")
                    for f in failed:
                        print(f"\t{f}")

    def __str__(self):
        out = f"\nResourceManager #{self.id} {70 * '='}\n"
        out += f"name: {self.name}\n"
        out += f"local directory: {self.tempDir}\n"
        out += f"keep stored files: {'yes' if self.keepFiles else 'no'}\n"
        out += f"space occupied: {get_formated_file_size(self.tempDir)}\n"
        out += f"DOI: {self.__doi}\n" if self.__doi is not None else f"no DOI assigned\n"
        out += f"{90 * '='}\n"
        return out

    def updateDBrecord(self):
        newValues = {"name": self.name, "doi": self.__doi, "files_stored": self.keepFiles, }
        self.dbconnection.updateResourceManager(self, **newValues)
        # for cont in self.containerTree:
        #     cont.updateDBrecord(self.dbconnection)



    def setDOI(self, doi):
        """
        Changes the DOI of a resource with all appropriate actions
        - reads the registration agency and publisher response metadata and assigns them to the ResourceManager
        - check for files bound to the DOI record
        - download the files (unpack archives if necessary)
        - create container tree from files
        - remove old files if there were any

        """
        # if the __doi parameter already had some value
        if self.__doi:
            # and the new value differs from the previous one
            if self.__doi != doi:
                # remove the files that were downloaded from the DOI record before
                self.deleteAllResourceFiles()
                pass
        # set the new DOI
        self.__doi = doi
        # populate the registration agency
        self.registrationAgency = ResourceManager.getRegistrationAgencyOfDOI(self.__doi)
        # populate the metadata properties
        self.DOImetadata = self.getDOImetadata(self.__doi)
        # append the DOI metadata JSON container to the resourceManagers containers
        self.containerTree.append(ContainerHandlerFactory().createHandler("json", "Resource DOI metadata JSON", self, self.DOImetadata))
        # populate publisher with Publisher class instance
        # try:
        self.publisher = self.getPublisher(self.DOImetadata)
        # except DOIdataRetrievalException:
        #     print(self.DOImetadata['publisher'])
        # else:
        # append the publisher metadata JSON container to the resourceManagers containers
        self.containerTree.append(ContainerHandlerFactory().createHandler("json", "{} metadata JSON".format(self.publisher.name), self, self.publisher.getMetadata()))
        # get downloadable files information from publisher
        self.publishedFiles = self.publisher.getFileInfo()

        # self.getMetadataFromPublisher()

        # self.getFileInfoFromPublisher()
        return

    def getDOI(self):
        """
        Private attribute __doi getter
        """
        return self.__doi


    def getAllFilesList(self):
        filesList = []
        for cont in self.containerTree:
            cont.listOwnFiles(filesList)
        return filesList

    def deleteAllResourceFiles(self):
        failed = []
        for cont in self.containerTree:
            cont.deleteOwnFiles(failed)
        if len(failed) > 0:
            flist = "\n".join([f"{f[0]}: {f[1]}" for f in failed])
            raise LocalFileManipulationError(f"Failed to delete following files:\n{flist}")
        else:
            print("All files successfully deleted.")
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
                    raise DOIdataRetrievalException(f"Unsupported data repository '{publisherKey}' - currently only implemented for Zenodo")


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
                if RAjson['status'] == "Invalid DOI":
                    raise DOIdataRetrievalException(f"Provided DOI '{doi}' is invalid.")
                if RAjson['status'] == "DOI does not exist":
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
        RA = ResourceManager.getRegistrationAgencyOfDOI(doi)
        if (RA == 'DataCite'):
            url = "https://api.datacite.org/dois/" + doi
            headers = {"accept": "application/vnd.api+json"}

            try:
                print("obtaining metadata from DOI registration agency ...")
                output = requests.get(url, headers=headers).json()

            except requests.exceptions.ConnectionError:
                print("A connection error occurred. Check your internet connection.")
            except requests.exceptions.Timeout:
                print("The request timed out.")
            except requests.exceptions.HTTPError as e:
                print("HTTP Error:", e)
            except requests.exceptions.RequestException as e:
                print("An error occurred:", e)
            else:
                if 'error' in output.keys():
                    raise DOIdataRetrievalException("Registration agency '{}' didn't respond. Error {}: {}".format(ResourceManager.getRegistrationAgencyOfDOI(doi), output['status'], output['error']))
                print(" ... successful\n")
                return output
        else:
            print("Unsupported registration agency '{}'".format(RA))
            raise DOIdataRetrievalException("Unsupported registration agency '{}'".format(RA))
            return None

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

                if not os.path.isdir(self.tempDir):
                    os.mkdir(self.tempDir)
                fileList = []
                if not list:
                    for sourceFile in self.publishedFiles:
                        url = sourceFile.source_url
                        # any file name manipulation can be performed here
                        filename = sourceFile.filename.replace("\\/<[^>]*>?", "_")

                        local_path = os.path.join(self.tempDir, filename)

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
                                newContainer = ContainerHandlerFactory().createHandler('filesystem', sourceFile.filename, self, None, path=local_path)
                                self.containerTree.append(newContainer)

                            else:
                                # something needs to be done if the response is not OK ...
                                print("\t\tThe response was not OK!")
                                sourceFile.local_path= None

                                return False

                print(" ... successful\n")
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
                return [ContainerHandlerFactory.getContainerByID(c) for c in cid]
            except:
                raise
        else:
            ContainerHandlerFactory.getContainerByID(cid)

    def newDataset(self, name):
        """
        Adds DatasetHandler instance to dataset list
        """
        new_dataset = Dataset(name)
        self.datasets.append(new_dataset)
        return new_dataset

    def addDataset(self, dataset):
        """
        Adds DatasetHandler instance to dataset list
        """
        self.datasets.append(dataset)
        return

    def removeDataset(self, index):
        """
        Removes DatasetHandler instance to dataset list
        """
        del self.datasets[index]

    def showContainerTree(self):
        """
        Induces printing contents of the whole container tree
        """
        print(80 * "=")
        print("{}\ncontainer tree:".format(self.name))
        print(80 * "-")
        for container in self.containerTree:
            container.showContents(0)
        print(80 * "=" + 5 * "\n")


    def showDatasetsContents(self):
        for ds in self.datasets:
            ds.showContents()
        return


class Dataset:
    """
    Represents a set of data containers that form together a distinct collection of data represented by a MetadataStructureMap.
    The instance has its own MetadataStructureMap that is being composed during the metadata generation phase
    """

    def __init__(self, name):
        # dataset name
        self.name = name
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
            containers = [containers_to_remove]
        self.containers = [con for con in self.containers if con not in containers_to_remove]
        return

    def showContainerTree(self):
        """
        Induces printing contents of the whole container tree
        """
        print(80 * "=")
        print(f"dataset\n'{self.name}'\ncontainer tree: ")
        print(80 * "-")
        for container in self.containers:
            container.showContents(0)
        print(80 * "=" + 2 * "\n")

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
    ContainerHandler object instances factory, global singleton - the only way to create container handlers
    Keeps track of all the ContainerHandler class and all subclass' instances created
    """

    # directory of registered containers types classes
    containerTypes = {}

    # the one and only instance
    _instance = None

    # dictionary of already created container handlers by ID
    containers = {}
    # class counter of ID to be assigned to next created ContainerHandler
    nextContainerID = 0

    @classmethod
    def getContainerByID(cls, cid):
        """
        Returns container of particular ID from inner dictionary
        """

        if cls.containers.get(cid):
            return cls.containers.get(cid)
        else:
            raise ContainerStructureError(f"Container id = {cid} was never created by this factory!")

    @classmethod
    def registerContainerType(cls, containerTypeClass, key):
        """
        Registers ContainerHandler subclasses in the factory
        """
        cls.containerTypes[key] = containerTypeClass
        print("DatasetHandler '{}' registered".format(key))
        return

    @classmethod
    def createHandler(cls, general_type, *args, **kwargs):
        """
        Creates and returns instance of ContainerHandler of given type
        Subclasses can implement further specialization of the type by overriding ContainerHandler.getSpecializedSubclassType()

        """
        # check if the requested container type is registered in the factory
        if general_type not in ContainerHandlerFactory.containerTypes.keys():
            raise ValueError("Unsupported container handler type '{}'. Supported are:"
                             " {}".format(general_type, ",".join( ["'" + k + "'" for k in cls.containerTypes.keys()])))
        else:
            # raise the ID for next container
            cls.nextContainerID += 1

            # get specialized subclass type
            specialized_type = cls.containerTypes[general_type].getSpecializedSubclassType(**kwargs)
            # check if the requested specialized container type is registered in the factory
            if specialized_type not in ContainerHandlerFactory.containerTypes.keys():
                raise ValueError("Unsupported container handler type '{}'. Supported are:"
                                 " {}".format(general_type, ",".join(["'" + k + "'" for k in cls.containerTypes.keys()])))

            # create new container instance with unique id in the ResourceManager scope
            new_container = cls.containerTypes[specialized_type](cls.nextContainerID, *args, **kwargs)
            # put it in the factory list
            cls.containers.update({new_container.id: new_container})
            return new_container

    def __init__(self):
        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance



class ContainerHandler:
    """
    Represents an enclosed data structure.
    It can be either a file or string or other data structure that can be manipulated and analyzed
    """
    containerType = None
    containerFormat = None
    keywordsDBname = None

    @classmethod
    def getSpecializedSubclassType(cls, **kwargs):
        """
        This method comes handy when one ContainerHandler subclass needs to control creation of own subclasses
        """
        return cls.containerType

    def __init__(self, id, name, resource_manager, parent_container=None):
        # unique ID in the ResourceManagers scope
        self.id = id
        # container name (filename/database name/table name ...)
        self.name = name
        # reference to the ResourceManager that the container belongs to
        self.resourceManager = resource_manager
        # parent container instance (if not root container)
        self.parentContainer = parent_container
        # data containers that the container contains
        self.containers = []
        # metadata entities that the container contains
        self.metadataElements = []
        # the crawler assigned to the container
        self.crawler = None

        # make the class properties accessible through instance properties
        self.containerType = type(self).containerType
        self.containerFormat = type(self).containerFormat
        self.keywordsDBname = type(self).keywordsDBname

    def __str__(self):
        out = f"\n|  # {self.id}  |  {type(self).__name__}\n|  {self.name}  \n"
        if hasattr(self, "path"):
            out += f"|  {self.path}"

        return out


    def showContents(self, depth = 0, ind = ". "):
        """
        Prints structured info about the container and invokes showContents on all of its containers

        :param depth: current depth of showKeyValueStructure recursion
        :param ind: string of a single level indentation
        """
        # get the indentation string
        t = ind * depth
        # print attributes of this container
        print("{}{} - {} ({}) [{}]".format(t, self.id, self.name, self.containerType, len(self.containers)))

        # invoke showContents of sub-containers
        if len(self.containers) > 0:
            depth += 1
            for cont in self.containers:
                cont.showContents(depth)

    def updateDBrecord(self, db_connection):
        if hasattr(self, "path"):
            path = self.path
        else:
            path = None

        newValues = {"id_local": self.id, "name": self.name, "parent_id": None, "resource_id": None, "path": path}
        db_connection.updateContainer(self.id, **newValues)
        return

    def createTree(self, *args):
        pass

    def getCrawled(self):
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
        else:
            newPublisher = cls.publishers[publisherKey](*args)
            cls.publishers.update({newPublisher.key: newPublisher})

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
    Points to an exact location in a dataset and defines a way to extract the value of a particular matedata entity instance.
    Concrete implementations defined in subclasses.
    """
    pass

class ResourcePointer(Pointer):
    """
    Pointer that is not related to any provided file/table.
    For metadata elements that are found/created for the ResourceManager.
    """

    pass

class Datasetpointer(Pointer):
    """
    Pointer that is not related to any provided file/table.
    For metadata elements that are created for the Dataset.
    """

    pass

class Crawler:
    """
    Top level abstract class of the metadata/data crawler
    """

    def __init__(self, container):
        self.container = container
        pass

    def crawl(self):
        """
        Parses the source and translate it to metadata elements structure
        :return: MetadataStructureMap
        """
        return


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

