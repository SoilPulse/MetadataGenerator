# coding = utf-8
# -*- coding: utf-8 -*-

import requests
import os
import shutil

from .metadata_scheme import MetadataStructureMap
from .db_access import DBconnector
from .exceptions import DOIdataRetrievalException, LocalFileManipulationError, ContainerStructureError

# general variables
downloadedFilesDir = "downloaded_files"
class ResourceManager:
    """
    Singleton for a running session (only one Resource can be edited and managed at a time)
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(ResourceManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, name = None, doi = None, id = None):
        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance

        def __init__(self, name=None, doi=None, id=None):
            if not hasattr(self, 'initialized'):  # Ensures __init__ is only called once
                self.dbconnection = DBconnector()
                if id is None:
                    # Create a new resource record in the database
                    self.id = self.dbconnection.createResourceRecord(name, doi)


                else:
                    # Load the existing resource from the database
                    self.id = id
                    self.loadResource(id)


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
        # dedicated directory where files can be stored
        self.tempDir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), downloadedFilesDir, str(self.id))
        # language of the resource
        self.language = None

        if doi:
            self.setDOI(doi)

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
        self.containerTree.append(ContainerHandlerFactory().createHandler("json", "Resource DOI metadata JSON", self.DOImetadata))
        # populate publisher with Publisher class instance
        # try:
        self.publisher = self.getPublisher(self.DOImetadata)
        # except DOIdataRetrievalException:
        #     print(self.DOImetadata['publisher'])
        # else:
        # append the publisher metadata JSON container to the resourceManagers containers
        self.containerTree.append(ContainerHandlerFactory().createHandler("json", "{} metadata JSON".format(self.publisher.name), self.publisher.getMetadata()))
        # get downloadable files information from publisher
        self.publishedFiles = self.publisher.getFileInfo()


        # self.getMetadataFromPublisher()

        # self.getFileInfoFromPublisher()


    def getDOI(self):
        """
        Private attribute __doi getter
        """
        return self.__doi

    def deleteAllResourceFiles(self):
        failed = 0
        for file in self.sourceFiles:
            print(file)
            filename = os.path.basename(file['local_path'])
            try:
                os.remove(file['local_path'])
                print("File '{}' successfully deleted.".format(filename))
            except:
                raise LocalFileManipulationError("Failed to delete '{}' from local files storage '{}'."
                                                 .format(os.path.basename(file['local_path']),
                                                         os.path.dirname(file['local_path'])))
                failed += 1

        if failed > 0:
            return False
        return True

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
                return None


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
        :return: dictionary of file types for input URLs
        """

        if len(self.publishedFiles) == 0:
            print("The list of published files is empty.\n")
        else:
            # create the target directory if not exists
            print("downloading remote files to local storage ('{}') ...".format(self.tempDir))

            if not os.path.isdir(self.tempDir):
                os.mkdir(self.tempDir)
            result = {}
            if not list:
                for sourceFile in self.publishedFiles:
                    url = sourceFile.source_url
                    # any file name manipulation can be performed here
                    filename = sourceFile.filename.replace("\\/<[^>]*>?", "_")

                    local_path = os.path.join(self.tempDir, filename)

                    try:
                        response = requests.get(url+"/content")
                    except requests.exceptions.ConnectionError:
                        print("\tA connection error occurred. Check your internet connection.")
                        return False
                    except requests.exceptions.Timeout:
                        print("\tThe request timed out.")
                        return False
                    except requests.exceptions.HTTPError as e:
                        print("\tHTTP Error:", e)
                        return False
                    except requests.exceptions.RequestException as e:
                        print("\tAn error occurred:", e)
                        return False
                    else:
                        if response.ok:
                            with open(local_path, mode="wb") as filesave:
                                filesave.write(response.content)

                            # on success save local path of downloaded file to its attribute
                            sourceFile.local_path = local_path

                            # TODO - this should be implemented better, the container type distribution should be defined without using the explicit type strings ... so far I don't know how to achieve it
                            # create a container from the file with all related actions
                            if os.path.isdir(local_path):
                                newContainer = ContainerHandlerFactory().createHandler('directory', sourceFile.filename, local_path)
                            else:
                                extension = local_path.split(".")[-1]
                                if extension in get_supported_archive_formats() or extension == "gz":
                                    newContainer = ContainerHandlerFactory().createHandler('archive', sourceFile.filename, local_path)
                                else:
                                    newContainer = ContainerHandlerFactory().createHandler('file', sourceFile.filename, local_path)
                            self.containerTree.append(newContainer)

                        else:
                            # something needs to be done if the response is not OK ...
                            print("\t\tThe response was not OK!")
                            sourceFile.local_path= None

                            return False

            print(" ... successful\n")
            return result


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
    Container object factory
    """

    # directory of registered containers types classes
    containerTypes = {}

    # the one and only instance
    _instance = None

    containers = {}
    nextContainerID = 1

    def __init__(self):
        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance
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
        cls.containerTypes[key] = containerTypeClass
        print("DatasetHandler '{}' registered".format(key))
        return

    @classmethod
    def createHandler(cls, containerType, *args):
        """
        Creates and returns instance of Container of given type
        Keeps track of all the instances created
        """
        if containerType not in ContainerHandlerFactory.containerTypes.keys():
            raise ValueError("Unsupported container handler type '{}'. Supported are: {}".format(containerType, ",".join(["'"+k+"'" for k in cls.containerTypes.keys()])))
        else:
            # create new container instance with unique id in the ResourceManager scope
            new_container = cls.containerTypes[containerType](cls.nextContainerID, *args)
            # put it in the factory list
            cls.containers.update({new_container.id: new_container})
            # raise the ID for next container
            # print(f"adding container of type '{containerType}'")
            # print(args)
            cls.nextContainerID += 1
            # print(f"next id = {cls.nextContainerID}")
            return new_container


class ContainerHandler:
    """
    Represents a single data container (file/db/table ) that can be crawled and analyzed
    """
    containerType = None
    containerFormat = None
    keywordsDBname = None

    def __init__(self, id, name):
        # unique ID in the ResourceManagers scope
        self.id = id
        # container name (filename/database name/table name ...)
        self.name = name
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

    def showContents(self, depth = 0, ind = ". "):
        """
        Prints basic info about the container and invokes showContents on all of its containers

        :param depth: current depth of showKeyValueStructure recursion
        :param ind: string of a single level indentation
        """
        # get the indentation string
        t = ind * depth
        # print attributes of this container
        print("{}{} - {} ({}) [{}]".format(t, self.id, self.name, self.containerType, len(self.containers)))

        # invoke showContents of sub-containers
        if self.containers:
            depth += 1
            for cont in self.containers:
                cont.showContents(depth)

    def createTree(self):
        pass

    def getCrawled(self):
        pass

    def assignCrawler(self, crawler):
        self.crawler = crawler


class PublisherFactory:
    """
    Publisher object factory
    """

    # directory of registered publisher types classes
    publishers = {}

    # the one and only instance
    _instance = None
    def __init__(self):

        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance

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
            raise ValueError("Unsupported publisher handler type '{}'.\nRegistred data publishers are: {}".format(publisherKey, ",".join(["'"+k+"'" for k in cls.publishers.keys()])))
        else:
            newPublisher = cls.publishers[publisherKey](*args)
            cls.publishers.update({newPublisher.key: newPublisher})

            return newPublisher

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

def get_supported_archive_formats():
    """
    Return list of currently supported formats of shutil.unpack_archive() method.
    The extensions are stripped of the leading '.' so it can be compared to file extensions gained by .split('.')
    """
    archive_ext_list = []
    for format in shutil.get_unpack_formats():
        archive_ext_list.extend([ext.strip(".") for ext in format[1]])
    return archive_ext_list
