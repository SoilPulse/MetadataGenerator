# coding = utf-8
# -*- coding: utf-8 -*-

from ..project_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler
from ..db_access import EntityKeywordsDB


class XMLContainer(ContainerHandler):
    containerType = 'xml'
    containerFormat = "XML"
    keywordsDBname = "keywords_xml"

    # dictionary of DB fields needed to save this subclass instance attributes
    DBfields = {}
    # dictionary of attribute names to be used for DB save/update - current values need to be obtained at right time before saving
    serializationDict = {}

    def __init__(self, id, name):
        super(XMLContainer, self).__init__(id, name)
        self.crawler = XMLcrawler(self)


    def showContents(self):
        pass

    def getCrawled(self):
        pass

ContainerHandlerFactory.registerContainerType(XMLContainer, XMLContainer.containerType)
EntityKeywordsDB.registerKeywordsDB(XMLContainer.containerType, XMLContainer.keywordsDBname)

class XMLPointer(Pointer):
    pass

class XMLcrawler(Crawler):
    def __init__(self, container):
        self.container = container
        # print(f"\tXML crawler created for container #{self.container.id} '{self.container.name}' (file '{self.container.path}')")
        pass

    def crawl(self):
        print("No crawling procedure defined yet for XML crawler")
        pass