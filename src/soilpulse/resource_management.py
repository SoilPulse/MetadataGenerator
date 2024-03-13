# coding = utf-8
# -*- coding: utf-8 -*-

import requests
import os

from .metadata_scheme import MetadataStructureMap
from .exceptions import DOIdataRetrievalException

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
        # dictionary of source files that were added to the resource by any way
        self.sourceFiles = {}
        # the tree structure of included files and other container types
        self.containerTree = None
        # the DOI is private so it can't be changed without consequences - only setDOI(doi) can be used
        self.__doi = doi
        # dedicated directory where files can be stored
        self.tempDir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "downloaded_files")
        # language of the resource
        self.language = None

        if doi:
            self.setDOI(doi)

    def setDOI(self, doi):
        # if the __doi parameter already had some value
        if self.__doi:
            # and the new value differs from the previous one
            if self.__doi != doi:
                # remove the files that were downladed from the DOI record before

                pass
        # set the new DOI
        self.__doi = doi
        # populate the metadata properties
        self.getMetadataFromDOI()
        # download data
        self.getDataOfDOI()

    def getDOI(self):
        return self.__doi
    def getMetadataFromDOI(self):

        pass
    def getDataOfDOI(self):
        try:
            metadataJSON = self.getMetadataJSON(self.__doi)
        except DOIdataRetrievalException as e:
            print("Error occured while retrieving metadata.")
            print(e.message)
            return None
        else:
            self.publisher = metadataJSON['data']['attributes']['publisher']

            if self.publisher == "Zenodo":
                zenodo_id = metadataJSON['data']['attributes']['suffix'].split(".")[-1]
                self.sourceFiles = self.getFileInfoFromZenodo(zenodo_id)
            else:
                raise DOIdataRetrievalException("Unsupported data repository - currently only implemented for Zenodo")
            # TODO implement other data providers

            print(self.sourceFiles)
            # download the files
            self.downloadFiles(self.sourceFiles)

        return

    @staticmethod
    def getRAofDOI(doi, meta=False):
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
            print("A connection error occurred. Check your internet connection.")
        except requests.exceptions.Timeout:
            print("The request timed out.")
        except requests.exceptions.HTTPError as e:
            print("HTTP Error:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
        else:
            # print("\t... successful")
            pass

        if not RAjson:
            raise DOIdataRetrievalException("Invalid DOI provided, or DOI not registered '{}'".format(doi))
        else:
            if (meta):
                return RAjson
            else:
                return RAjson[0]['RA']

    @staticmethod
    def getMetadataJSON(doi):
        """
        Get metadata in JSON from registration agency for provided DOI

        :param doi: doi string of the resource
        :return: json of metadata
        """
        # TODO implement other metadata providers
        RA = ResourceManager.getRAofDOI(doi)
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
                if output['error']:
                    raise DOIdataRetrievalException("Registration agency '{}' doesn't respond. Error {}: {}".format(ResourceManager.getRAofDOI(doi), output['status'], output['error']))
                    return None
                print("\t... successful\n")
                return output
        else:
            print("Unsupported registration agency '{}'".format(RA))
            # raise DOIdataRetrievalException("Unsupported registration agency '{}'".format(RA))

    @staticmethod
    def getFileInfoFromZenodo(zenodo_id):
        """
        Collect resource files information from Zenodo record

        :param zenodo_id: Zenodo record identifier
        :return: dictionary of file info [{filename: name of the file, id: file id, size: file size, checksum: checksum, source_url: download link, local_path: path to local copy}, ...]
        """

        try:
            print("obtaining file information from Zenodo ...")
            response = requests.get("https://zenodo.org/api/records/" + zenodo_id).json()

        except requests.exceptions.ConnectionError:
            print("A connection error occurred. Check your internet connection.")
        except requests.exceptions.Timeout:
            print("The request timed out.")
        except requests.exceptions.HTTPError as e:
            print("HTTP Error:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
        else:

            URLroot = response['links']['files']
            if isinstance(response['files'], list):
                allFilesInfo = []
                for i in range(0, len(response['files'])):
                    fileinfo = {}
                    key = response['files'][i]['key']
                    id = response['files'][i]['id']
                    size = response['files'][i]['size']
                    checksum = response['files'][i]['checksum']
                    source_url = URLroot+"/"+key
                    fileinfo.update({'filename': key, 'id': id, 'size': size, 'checksum': checksum, 'source_url': source_url, 'local_path': None})

                allFilesInfo.append()
                print("\t... successful")
                return (allFilesInfo)
            else:
                raise DOIdataRetrievalException(
                    "Dataset files can not be retrieved - incorrect response structure.")
                return None

    def downloadFiles(self, unzip=True):
        """
        Download files from url list and unzips zip files.

        :param url_dict: dictionary of urls to be downloaded, filename is the key
        :param target_dir: local directory that will be used to download and optionally extract archives
        :param unzip: if the downloaded file is a .zip archive it will be extracted if unzip=True

        :return: dictionary of file types for input URLs
        """
        # create the target directory if not exists
        if not os.path.isdir(self.tempDir):
            os.mkdir(self.tempDir)

        result = {}
        for sourceFile in self.sourceFiles:
            url = sourceFile['source_url']
            print(url)
            # url_host = "/".join(url.split("/")[0:3])
            file_name = url.split("/")[-1].split("?")[0]
            # print("downloading file '{}' from {}.".format(file_name, url_host))
            local_file_path = os.path.join(self.tempDir, sourceFile['key'])
            sourceFile.upddate({'local_path': local_file_path})
            try:
                # print("/".join(url.split("/")[:-1]))
                # response = requests.get("/".join(url.split("/")[:-1]))
                response = requests.get(url+"/content")
            except requests.exceptions.ConnectionError:
                print("\t\tA connection error occurred. Check your internet connection.")
                return False
            except requests.exceptions.Timeout:
                print("\t\tThe request timed out.")
                return False
            except requests.exceptions.HTTPError as e:
                print("\t\tHTTP Error:", e)
                return False
            except requests.exceptions.RequestException as e:
                print("\t\tAn error occurred:", e)
                return False
            else:
                # the parameter download = 1 is specific to Zenodo
                if response.ok:
                    with open(local_file_path, mode="wb") as filesave:
                        filesave.write(response.content)
                else:
                    # something needs to be done if the response is not OK ...
                    print("\t\tThe response was not OK!")
                    return False

                if (local_file_path.endswith(".zip") and unzip):
                    self.extractZipFile(local_file_path)
                    result[url] = "unzipped zip file"
                else:
                    result[url] = "raw file"
        print("\t... successful")
        return result

    def extractZipFile(self, theZip, targetDir = None):
        from zipfile import ZipFile

        outDir = targetDir if targetDir else os.path.dirname(theZip)
        try:
            print("extracting '{}'".format(theZip))
            with ZipFile(theZip) as my_zip_file:
                my_zip_file.extractall(outDir)
        except ZipFile.BadZipfile:
            print("File '{}' is not a valid ZIP archive and couldn't be extracted".format(theZip))
        else:
            try:
                os.remove(theZip)
            except OSError:
                print("\nFile '{}' couldn't be deleted. It may be locked by another application.".format(theZip))


    def create_tree(self, sub_folder_dict):
        tree = []
        for k, v in sub_folder_dict.items():
            tree.append(self.create_node(k, v, sub_folder_dict))
        return tree

    def create_node(self, abs_path, sub_folders, sub_folder_dict):
        node = {"label": abs_path.split('\\')[-1], "value": abs_path}
        if sub_folders:
            node["children"] = []
            for sub_folder in sub_folders:
                abs_path = os.path.join(abs_path, sub_folder)
                # if os.path.isdir(abs_path):
                node["children"].append(self.create_node(abs_path, sub_folder_dict.get(abs_path, []), sub_folder_dict))
        return node

    def showContents(self):
        print("{}:".format(self.name))
        print(self.sourceURLs)

    def scanFileStructure(self, directory):
        """
        scans a parent directory to fill inner properties
        """
        return


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

    def showContents(self):
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

    _instance = None
    def __init__(self, uri):
        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance

    @classmethod
    def registerContainerType(cls, containerTypeClass, key):
        cls.containerTypes[key] = containerTypeClass
        # print("DatasetHandler of type '{}' registered".format(key))
        return

    @classmethod
    def createHandler(cls, containerType, *args):
        if containerType not in cls.containerTypes.keys():
            raise ValueError("Unsupported dataset handler type '{}'".format(containerType))
        else:
            return cls.datasetTypes[containerType](*args)

class ContainerHandler:
    """
    Represents a single data container (file/db table) that can be crawled and analyzed
    """
    containerType = None
    containerFormat = None
    keywordsDBname = None

    def __init__(self, name):
        # container name (filename/database name/table name ...)
        self.name = name
        # data containers that the container containes
        self.containers = []


    def showContents(self, depth = 0):
        print(self.name)
        depth += 1
        for cont in self.containers:
            cont.showContents(depth)

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
