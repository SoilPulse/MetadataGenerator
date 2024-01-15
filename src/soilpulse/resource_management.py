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
        # the singleton instance of the metadata mapping
        self.metadataScheme = MetadataStructureMap

class Repository:

    def __init__(self):
        # list of Dataset class instances contained within this repository
        self.resources = []
        pass

    def getType(self):
        pass

class Dataset:
    """
    This represents a set of data with consistent structure saved in a particular format
    """
    def __init__(self):
        # elements that
        self.containers = []

        self.metadataImage = MetadataStructureMap

class FileSystemRepository(Repository):
    def __init__(self):
        # list of all the directories that belong to the repository
        self.directories = []
        # list of all the files that belong to the repository
        self.files = []
        pass

class DatabaseRepository(Repository):
    pass

class XMLrepository(Repository):
    pass