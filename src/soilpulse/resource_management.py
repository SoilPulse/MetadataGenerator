# coding = utf-8
# -*- coding: utf-8 -*-

class ResourceManager:
    """
    Single instance for a particular resource (RunoffDB
    """
    def __init__(self, uri):
        self.URI = uri
        # list of Repository class instances contained within this resource
        self.repositories = []

class Repository:

    def __init__(self):
        # list of Dataset class instances contained within this repository
        self.datasets = []
        pass

class Dataset:

    def __init__(self):
        #
        self.containers = []

        self.metadataImage

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