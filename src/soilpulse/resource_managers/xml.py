# coding = utf-8
# -*- coding: utf-8 -*-

from src.soilpulse.resource_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler
from src.soilpulse.db_access import EntityKeywordsDB

type = 'xml'
format = "XML"
keywordsDBfilename = "keywords_xml"

class XMLContainer(ContainerHandler):
    containerType = type
    containerFormat = format
    keywordsDBname = keywordsDBfilename

    def __init__(self, name, doi = None):
        super(XMLContainer, self).__init__(name, doi)

    def showContents(self):
        pass

ContainerHandlerFactory.registerContainerType(XMLContainer, XMLContainer.containerType)
EntityKeywordsDB.registerKeywordsDB(XMLContainer.containerType, XMLContainer.keywordsDBname)

class XMLPointer(Pointer):
    pass

class XMLcrawler(Crawler):
    pass
