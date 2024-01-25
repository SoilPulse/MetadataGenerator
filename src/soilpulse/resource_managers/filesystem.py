# coding = utf-8
# -*- coding: utf-8 -*-

from src.soilpulse.resource_management import DatasetHandler, DatasetHandlerFactory, Pointer, Crawler

# just for the standalone functions - will be changed
from src.soilpulse.resource_management import *


class FileSystemDataset(DatasetHandler):
    datasetFormat = "File system"
    def __init__(self, name, doi=None):
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


class FilesystemCrawler(Crawler):
    """
    Crawler for file system repositories
    """

    pass
