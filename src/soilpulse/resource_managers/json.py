# coding = utf-8
# -*- coding: utf-8 -*-



from src.soilpulse.resource_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler
from src.soilpulse.db_access import EntityKeywordsDB
# just for the standalone functions - will be changed
from src.soilpulse.resource_management import *

type = 'json'
format = "JSON"
keywordsDBfilename = "keywords_json"

class JSONContainer(ContainerHandler):
    containerType = type
    containerFormat = format
    keywordsDBname = keywordsDBfilename

    def __init__(self, name, content):
        super(JSONContainer, self).__init__(name)
        # the file type
        self.content = content

    def showContents(self, t = ""):
        """
        Print basic info about the container and invokes showContents on all of its containers
        """

        print("{}{} - {} ({}) [{}]".format(t, self.id, self.name, self.containerType, len(self.containers)))
        t += "\t"

        for cont in self.containers:
            cont.showContents(t)

ContainerHandlerFactory.registerContainerType(JSONContainer, JSONContainer.containerType)
EntityKeywordsDB.registerKeywordsDB(JSONContainer.containerType, JSONContainer.keywordsDBname)

class JSONPointer(Pointer):

    pointerType = type

    def __init__(self, filename, startChar, numChars):

        pass


class JSONCrawler(Crawler):
    """
    Crawler for file system repositories
    """

    def __init__(self):
        pass

    def crawl(self):
        """
        Do the crawl - go through the file and detect defined elements
        """
        pass
