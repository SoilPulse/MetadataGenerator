# coding = utf-8
# -*- coding: utf-8 -*-

import requests
import os

from .metadata_scheme import MetadataStructureMap
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
    try:
        print("obtaining DOI registration agency ...")
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
        print("\t... successful")

    if not RAjson or 'status' in RAjson[0]:
        raise DOIdataRetrievalException("Invalid DOI provided, or DOI not registered '{}'".format(doi))
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
    # TODO implement other metadata providers

    if (getRAofDOI(doi) == 'DataCite'):
        url = "https://api.datacite.org/dois/" + doi
        headers = {"accept": "application/vnd.api+json"}

        try:
            print("obtaining metadata from DOI registrar ...")
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
            print("\t... successful")

        return output
    else:
        raise DOIdataRetrievalException('Unsupported registration agency')

def getFileListOfDOI(doi):
    """
    Get list of files associated with given DOI.

    :param doi: doi string of the resource
    :return: list of files
    """
    # TODO implement other data providers

    metadataJSON = getMetadataJSON(doi)
    datasetURL = metadataJSON['data']['attributes']['url']

    if "zenodo.org" in datasetURL:
        zenodo_id = datasetURL.split("/")[-1].split(".")[-1]
        #    print("retrieving information for Zenodo dataset: "+zenodo_id)

        try:
            print("obtaining data from Zenodo ...")
            response = requests.get(
                "https://zenodo.org/api/records/" +
                zenodo_id + "/files").json()

        except requests.exceptions.ConnectionError:
            print("A connection error occurred. Check your internet connection.")
        except requests.exceptions.Timeout:
            print("The request timed out.")
        except requests.exceptions.HTTPError as e:
            print("HTTP Error:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
        else:
            print("\t... successful")

            if isinstance(response, list):
                linklist = [z['links']['content'] for z in response['entries']]
                return (linklist)
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
        # dedicated directory where files can be stored
        self.tempDir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "downloaded_files")
        # language of the resource
        self.language = None

        if doi:
            newDataset = DatasetHandlerFactory.createHandler('filesystem', name, self.tempDir, doi)

            self.addDataset(newDataset)

    def downloadFilesFromURL(self, url):
        """
        handles all needed steps to download (unpack archives if necessary) and create file structure tree
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
    def registerDatasetType(cls, datasetTypeClass, key):
        cls.datasetTypes[key] = datasetTypeClass
        # print("DatasetHandler of type '{}' registered".format(key))
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
    The instance has its own MetadataStructureMap that is being composed during the metadata generation phase
    """
    datasetType = None
    datasetFormat = None
    keywordsDBname = None

    def __init__(self, name, doi = None):
        # dataset name
        self.name = name
        # DOI if has any
        self.doi = doi
        # data containers that the dataset consists of
        self.containers = []
        # the instance of the metadata mapping
        self.metadataMap = MetadataStructureMap()



    def showContents(self):

        pass
    def checkMetadataStructure(self):
        self.metadataMap.checkConsistency()


class Pointer:
    """
    Points to an exact location in a dataset and defines a way to extract the value of a particular matedata entity instance.
    Concrete implementations defined in subclasses.
    """
    pass

class SessionPointer(Pointer):
    """
    Pointer that is not related to any provided file/table.
    For metadata elements that are established directly by the user within a session.
    """

    pass

class Crawler:
    """
    Top level abstract class of the metadata/data crawler
    """

    def __init__(self, resurceURI):
        self.resourceURI = resurceURI
        pass

    def getMetadataStructure(self):
        """
        Parses the source and translate it to metadata elements structure
        :return:
        """
        return
