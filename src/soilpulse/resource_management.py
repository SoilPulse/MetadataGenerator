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

    if not RAjson:
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

        # arbitrary resurce name for easy identification
        self.name = name
        # list of Dataset class instances contained within this resource
        self.datasets = []

        self.doi = doi
        self.URI = uri
        # dedicated directory where files can be stored
        self.tempDir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "downloaded_files")
        # language of the resource
        self.language = None

        if doi:

            newDataset = Dataset(name)

            self.addDataset(newDataset)

    def downloadFiles(self, url_list, target_dir, unzip=True):
        """
        Download files from url list and unzips zip files.

        :param url_list: list of urls to be downloaded
        :param target_dir: local directory that will be used to download and optionally extract archives
        :param unzip: if the downloaded file is a .zip archive it will be extracted if unzip=True

        :return: dictionary of file types for input URLs
        """
        # create the target directory if not exists
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

        result = {}
        for url in url_list:
            url_host = "/".join(url.split("/")[0:3])
            file_name = url.split("/")[-1].split("?")[0]
            print("downloading file '{}' from {}.".format(file_name, url_host))
            local_file_path = os.path.join(target_dir, file_name)
            try:
                response = requests.get(url, params={"download": "1"})
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

                if (file_name.endswith(".zip") and unzip):
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

    def crawl(self):
        """
        Parses the source and translate it to metadata elements structure
        :return: MetadataStructureMap
        """
        return
