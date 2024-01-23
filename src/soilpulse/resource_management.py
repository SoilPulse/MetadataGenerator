# coding = utf-8
# -*- coding: utf-8 -*-

import requests

from .metadatascheme import MetadataStructureMap
from .exceptions import DOIdataRetrievalException

# general functions declaration
def getRAofDOI(doi, meta=False):
    """
    Get registration agency from doi.org API.

    :param doi: the DOI string of a published dataset (10.XXX/XXXX).
    :param meta: true to return whole json, false to return only a string of registration agency

    :return: complete registration agency json if meta = True, else registration agency name string
    """
    url = "https://doi.org/ra/" + doi
    RAjson = requests.get(url).json()
    if not RAjson:
        raise DOIdataRetrievalException("Invalid DOI provided, or DOI not registred '{}'".format(doi))
    else:
        if (meta):
            return RAjson
        else:
            return RAjson[0]['RA']


def getMetadataJSON(doi):
    """
    Get metadata in JSON from registration agency for provided DOI

    :param doi: doi string of the resource
    :return: json of metadata
    """
    if (getRAofDOI(doi) == 'DataCite'):
        url = "https://api.datacite.org/dois/" + doi
        headers = {"accept": "application/vnd.api+json"}

        return requests.get(url, headers=headers).json()
    else:
        raise DOIdataRetrievalException('Unsupported registration agency')

def getFileListOfDOI(doi):
    """
    Get list of files associated with given DOI.

    :param doi: doi string of the resource
    :return: list of files
    """
    metadataJSON = getMetadataJSON(doi)
    datasetURL = metadataJSON['data']['attributes']['url']

    if "zenodo.org" in datasetURL:
        zenodo_id = datasetURL.split("/")[-1].split(".")[-1]
        #    print("retrieving information for Zenodo dataset: "+zenodo_id)
        response = requests.get("https://zenodo.org/api/deposit/depositions/" + zenodo_id + "/files").json()
        if isinstance(response, list):
            fileList = []
            for file in response:
                if file['filename'].endswith(".zip"):
                    fileList.append(
                        "https://zenodo.org/records/" + zenodo_id
                        + "/files/" + file['filename'] + "?download=1"
                    )
            return (fileList)
        else:
            raise DOIdataRetrievalException("Dataset files can not be retrieved - incorrect response structure.")
    else:
        raise DOIdataRetrievalException("Unsupported data repository - currently only implemented for Zenodo")


class ResourceManager:
    """
    Singleton for a given resource
    """
    _instance = None
    def __init__(self, name = None, doi = None, uri = None):
        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance

        # list of Dataset class instances contained within this resource
        self.datasets = []
        self.name = name
        self.doi = doi
        self.URI = uri
        if doi:
            dataset = DatasetHandlerFactory.createHandler('filesystem', name, doi)
            self.datasets.append(dataset)

    def showContents(self):
        for ds in self.datasets:
            ds.showContents()
        return

class DatasetHandlerFactory:
    """
    Dataset object factory
    """

    # directory of registered dataset types classes
    datasetTypes = {}

    _instance = None
    def __init__(self, uri):
        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance

    @classmethod
    def registerDatasetType(cls, datasetTypeClass, kye):
        cls.datasetTypes[kye] = datasetTypeClass
        return

    @classmethod
    def createHandler(cls, datasetType, *args):
        if datasetType not in cls.datasetTypes.keys():
            raise ValueError("Unsupported dataset handler type '{}'".format(datasetType))
        else:
            return cls.datasetTypes[datasetType](*args)


class DatasetHandler:
    """
    Represents a set of data with consistent structure saved in a particular format.
    The
    """
    def __init__(self, name, doi = None):
        # dataset name
        self.name = name
        # DOI if has any
        self.doi = doi
        # data containers that the dataset consists of
        self.containers = []
        # the instance of the metadata mapping
        self.metadataImage = MetadataStructureMap
    def showContents(self):
        pass

class FileSystemDataset(DatasetHandler):
    datasetFormat = "File system"
    def __init__(self, name, doi = None):
        super(FileSystemDataset, self).__init__(name, doi)
        # list of all the directories that belong to the repository
        self.directories = []
        # list of all the files that belong to the repository
        self.files = []
        # directory where the script will have access to write
        self.tempDir = None

        if doi:
            self.files.extend(getFileListOfDOI(doi))

    def downloadFiles(self, URLlist):
        for url in URLlist:
            try:
                # download a single request
                pass
            except:

                pass
            else:

                pass
    def showContents(self):
        print("{}:".format(self.name))
        print(self.files)

    def unzipToDir(self, zipfile, targetDir):

        return

    def scanFileStructure(self, directory):
        """
        scans a parent directory to fill inner properties
        """
        return

DatasetHandlerFactory.registerDatasetType(FileSystemDataset, "filesystem")

class DatabaseDataset(DatasetHandler):
    datasetFormat = "Database"
    def __init__(self, name, doi = None):
        super(DatabaseDataset, self).__init__(name, doi)
        self.databaseName = None
        self.tables = []
        self.foreignKeys = []

    def showContents(self):
        pass
DatasetHandlerFactory.registerDatasetType(DatabaseDataset, "database")

class XMLDataset(DatasetHandler):
    datasetFormat = "XML"
    def __init__(self, name, doi = None):
        super(DatabaseDataset, self).__init__(name, doi)

    def showContents(self):
        pass

DatasetHandlerFactory.registerDatasetType(XMLDataset, "xml")

class Pointer:
    """
    Points to an exact location in a dataset and defines a way to extract the value of a particular matedata entity instance.
    Concrete implementation defined in subclasses.
    """
    pass

class FileSystemPointer(Pointer):
    def __init__(self, filename, start, length):
        # full path to the file of appearance
        self.filename = filename
        # index of place where the value starts
        self.start = start
        # length of the value in characters
        self.length = length
        pass

    pass

class DatabasePointer(Pointer):
    pass

class XMLPointer(Pointer):
    pass