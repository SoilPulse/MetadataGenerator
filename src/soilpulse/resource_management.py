# coding = utf-8
# -*- coding: utf-8 -*-

import requests

from .metadatascheme import MetadataStructureMap
from .exceptions import DOIdataRetrievalException

class ResourceManager:
    """
    Singleton for a given resource
    """
    _instance = None
    def __init__(self, doi = None, uri = None):
        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance

        # list of Dataset class instances contained within this resource
        self.datasets = []
        self.doi = doi
        self.URI = uri

    @classmethod
    def getRAofDOI(doi, meta=False):
        """
        Get registration agency from doi.org API.

        Parameters
        ----------
        :param doi: the DOI string of a published dataset (10.XXX/XXXX).
        :param meta: true to return whole json only a string of registration agency

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

    @classmethod
    def getMetadataJSON(doi):
        """
        Get metadata from registration agency for DOI in JSON

        :param doi: doi string of the resource
        :return: json of metadata
        """
        if (ResourceManager.getRAofDOI(doi) == 'DataCite'):
            url = "https://api.datacite.org/dois/"+doi
            headers = {"accept": "application/vnd.api+json"}

            return (requests.get(url, headers=headers).json())
        else:
            raise DOIdataRetrievalException('Unsupported registration agency')

    @classmethod
    def getFileListOfDOI(doi):
        """
        Get list of files associated with the given DOI.

        :param doi: doi string of the resource
        :return: list of files
        """
        metadataJSON = ResourceManager.getMetadataJSON(doi)
        datasetURL = metadataJSON['data']['attributes']['url']

        if ("zenodo.org" in datasetURL):
            zenodo_id = datasetURL.split("/")[-1].split(".")[-1]
        #    print("retrieving information for Zenodo dataset: "+zenodo_id)
            response = requests.get("https://zenodo.org/api/deposit/depositions/"+zenodo_id+"/files").json()
            if (type(response) == dict):
                raise DOIdataRetrievalException("Data set can not be retrieved.")
            else:
                file_list = []
                for file in response:
                    if (".zip" in file['filename']):
                        file_list.append(
                            "https://zenodo.org/records/"+zenodo_id
                            + "/files/"+file['filename']+"?download=1"
                            )
            return (file_list)
        else:
            raise DOIdataRetrievalException("Unsupported data repository - currently only implemented for Zenodo")

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
    def createDatasetHandlerInstance(cls, datasetType, *args):
        if datasetType not in cls.datasetTypes.keys():
            raise ValueError("Unsupported dataset handler type '{}'".format(datasetType))
        else:
            return cls.datasetTypes[datasetType](*args)


class DatasetHandler:
    """
    Represents a set of data with consistent structure saved in a particular format.
    The
    """
    def __init__(self, doi = None):
        # DOI if has any
        self.doi = doi
        # data containers that the dataset consists of
        self.containers = []
        # the instance of the metadata mapping
        self.metadataImage = MetadataStructureMap

class FileSystemDataset(DatasetHandler):
    datasetFormat = "File system"
    def __init__(self, doi = None):
        super(FileSystemDataset, self).__init__(doi)
        # list of all the directories that belong to the repository
        self.directories = []
        # list of all the files that belong to the repository
        self.files = []
        pass
DatasetHandlerFactory.registerDatasetType(FileSystemDataset, "filesystem")

class DatabaseDataset(DatasetHandler):
    datasetFormat = "Database"
    def __init__(self, doi = None):
        super(DatabaseDataset, self).__init__(doi)
        self.databaseName = None
        self.tables = []
        self.foreignKeys = []
    pass
DatasetHandlerFactory.registerDatasetType(DatabaseDataset, "database")

class XMLDataset(DatasetHandler):
    datasetFormat = "XML"
    def __init__(self, doi = None):
        super(DatabaseDataset, self).__init__(doi)
    pass
DatasetHandlerFactory.registerDatasetType(XMLDataset, "xml")