# coding = utf-8
# -*- coding: utf-8 -*-

import requests
import os

from .metadata_scheme import MetadataStructureMap
from .exceptions import DOIdataRetrievalException, LocalFileManipulationError

class ResourceManager:
    """
    Singleton for a running session (only one Resource can be edited and managed at a time)
    """

    _instance = None
    def __init__(self, name = None, doi = None):
        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance

        # arbitrary resurce name for easy identification
        self.name = name

        # list of Dataset class instances contained within this resource
        self.datasets = []

        # registration agency of the DOI
        self.registrationAgency = None
        # metadata package from DOI record
        self.DOImetadata = None
        # publisher instance
        self.publisher = None
        # dictionary of source files that were added to the resource by any way
        self.filesOfDOI = {}
        # the tree structure of included files and other container types
        self.containerTree = []
        # the DOI is private so it can't be changed without consequences - only setDOI(doi) can be used
        self.__doi = doi
        # dedicated directory where files can be stored
        self.tempDir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "downloaded_files")
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
        self.containerTree.append(ContainerHandlerFactory.createHandler("json", "Resource DOI metadata JSON", self.DOImetadata))
        # populate publisher with Publisher class instance
        self.publisher = self.getPublisher(self.DOImetadata)
        # append the publisher metadata JSON container to the resourceManagers containers
        self.containerTree.append(ContainerHandlerFactory.createHandler("json", "{} metadata JSON".format(self.publisher.name), self.publisher.getMetadata()))
        # get downloadable files information
        self.filesOfDOI = self.publisher.getFileInfo()
        # download the files
        self.downloadFiles()

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

    def getMetadataFromPublisher(self):
        try:
            RAmetadata = self.getDOImetadata(self.__doi)
        except DOIdataRetrievalException as e:
            print("Error occurred while retrieving metadata.")
            print(e.message)
            return None
        else:
            publisher = RAmetadata['data']['attributes']['publisher']
            print("obtaining metadata from publisher ({}) ...".format(publisher))

            if publisher == "Zenodo":
                zenodo_id = RAmetadata['data']['attributes']['suffix'].split(".")[-1]
                self.publisher = PublisherFactory.createHandler(publisher, zenodo_id)
                self.sourceFiles = self.publisher.getFileInfo()
            else:
                raise DOIdataRetrievalException("Unsupported data repository - currently only implemented for Zenodo")
            # TODO implement other data providers
            print(" ... successful.\n")

        return

        pass

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
                print("Couldn't find publisher value in the DOI registration agency metadata respnse.")
                print(e.message)
            else:
                if publisherKey == "Zenodo":
                    zenodo_id = DOI_metadata['data']['attributes']['suffix'].split(".")[-1]
                    publisher = PublisherFactory.createHandler(publisherKey, zenodo_id)
                    return publisher
                else:
                    raise DOIdataRetrievalException("Unsupported data repository - currently only implemented for Zenodo")
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
                    # raise DOIdataRetrievalException("Invalid DOI provided, or DOI not registered '{}'".format(doi))
                    raise DOIdataRetrievalException("Provided DOI '{}' is invalid.".format(doi))
                    return None
                if RAjson['status'] == "DOI does not exist":
                    # raise DOIdataRetrievalException("Invalid DOI provided, or DOI not registered '{}'".format(doi))
                    raise DOIdataRetrievalException("Provided DOI '{}' is not registered.".format(doi))
                    return None
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
                    raise DOIdataRetrievalException("Registration agency '{}' doesn't respond. Error {}: {}".format(ResourceManager.getRegistrationAgencyOfDOI(doi), output['status'], output['error']))
                    return None
                print(" ... successful\n")
                return output
        else:
            print("Unsupported registration agency '{}'".format(RA))
            # raise DOIdataRetrievalException("Unsupported registration agency '{}'".format(RA))

    def downloadFiles(self):
        """
        Download files that are stored in self.sourceFiles dictionary.

        :return: dictionary of file types for input URLs
        """
        if len(self.filesOfDOI) == 0:
            print("The file list is empty.\n")
        else:
            # create the target directory if not exists
            print("downloading remote files to local storage ('{}') ...".format(self.tempDir))

            if not os.path.isdir(self.tempDir):
                os.mkdir(self.tempDir)
            result = {}
            for sourceFile in self.filesOfDOI:
                url = sourceFile['source_url']
                local_file_path = os.path.join(self.tempDir, sourceFile['filename'])

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
                    # the parameter download = 1 is specific to Zenodo
                    if response.ok:
                        with open(local_file_path, mode="wb") as filesave:
                            filesave.write(response.content)

                        # write local path of downloaded file to its dictionary
                        sourceFile['local_path'] = local_file_path

                        # create a container from the file with all related actions
                        newContainer = ContainerHandlerFactory.createHandler('filesystem', sourceFile['filename'], local_file_path)
                        self.containerTree.append(newContainer)

                    else:
                        # something needs to be done if the response is not OK ...
                        print("\t\tThe response was not OK!")
                        sourceFile['local_path'] = None

                        return False

            print(" ... successful\n")
            return result


    def uploadFilesFromSession(self, files):
        """
        handles all needed steps to upload files from a session (unpack archives if necessary) and create file structure tree
        """
        return


    def addDataset(self, dataset):
        """
        Adds DatasetHandler instance to dataset list
        """
        self.datasets.append(dataset)
        return

    def removeDatset(self, index):
        """
        Removes DatasetHandler instance to dataset list
        """
        del self.datasets[index]

    def showContainerTree(self):
        """
        Induces printing contents of the whole container tree
        """
        print("{}\ncontainer tree:".format(self.name))
        for container in self.containerTree:
            container.showContents(0)


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

    def showContents(self):

        pass

    def checkMetadataStructure(self):
        self.metadataMap.checkConsistency()

class ContainerHandlerFactory:
    """
    Container object factory
    """

    # directory of registered containers types classes
    containerTypes = {}
    # next container ID
    nextContainerID = 1
    # all the containers created so far
    containers = {}
    # the one and only instance
    _instance = None
    def __init__(self):
        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance


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
        if containerType not in cls.containerTypes.keys():
            raise ValueError("Unsupported container handler type '{}'. Supported are: {}".format(containerType, ",".join(["'"+k+"'" for k in cls.containerTypes.keys()])))
        else:
            # assign id to container - unique in the ResourceManager scope
            newContainer = cls.containerTypes[containerType](*args)
            newContainer.id = cls.nextContainerID
            cls.containers.update({newContainer.id: newContainer})
            cls.nextContainerID += 1
            return newContainer

class ContainerHandler:
    """
    Represents a single data container (file/db/table ) that can be crawled and analyzed
    """
    containerType = None
    containerFormat = None
    keywordsDBname = None

    def recognizeType(cls):
        pass
    def __init__(self, name):
        # unique ID in the ResourceManagers scope
        self.id = None
        # container name (filename/database name/table name ...)
        self.name = name
        # data containers that the container contains
        self.containers = []
        # metadata entities that the container contains
        self.metadataElements = []

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

        # invoke showContents of subcontainers
        if self.containers:
            depth += 1
            for cont in self.containers:
                cont.showContents(depth)

    def createTree(self):
        pass

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
    def registerPublisher(cls, publisherClass, key):
        cls.publishers[key] = publisherClass
        print("Publisher '{}' registered".format(key))
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

class FileArchiveContainer(ContainerHandler):
    containerType = "file_archive"
    containerFormat = "File Archive"

    def __init__(self, name, archive_type = None):
        super(FileArchiveContainer, self).__init__(name)
        self.archiveType = archive_type

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

    def __init__(self, resurceURI):
        self.resourceURI = resurceURI
        pass

    def crawl(self):
        """
        Parses the source and translate it to metadata elements structure
        :return: MetadataStructureMap
        """
        return
