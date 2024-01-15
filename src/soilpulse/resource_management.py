# coding = utf-8
# -*- coding: utf-8 -*-

from .metadatascheme import MetadataStructureMap

class ResourceManager:
    """
    Singleton for a given resource
    """
    _instance = None
    def __init__(self, uri):
        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance

        self.URI = uri
        # list of Dataset class instances contained within this resource
        self.datasets = []

class Dataset:
    """
    Represents a set of data with consistent structure saved in a particular format
    """
    def __init__(self):
        # data containers that the dataset consists of
        self.containers = []
        # the instance of the metadata mapping
        self.metadataImage = MetadataStructureMap

class FileSystemDataset(Dataset):
    datasetFormat = "File system"
    def __init__(self):
        # list of all the directories that belong to the repository
        self.directories = []
        # list of all the files that belong to the repository
        self.files = []
        pass

class DatabaseDataset(Dataset):
    datasetFormat = "Database"
    def __init__(self):
        self.databaseName = None
        self.tables = []
        self.foreignKeys = []
    pass

class XMLDataset(Dataset):
    datasetFormat = "XML"
    pass