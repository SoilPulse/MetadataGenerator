# coding = utf-8
# -*- coding: utf-8 -*-

from ..resource_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler
from ..db_access import EntityKeywordsDB


class XMLContainer(ContainerHandler):
    containerType = 'xml'
    containerFormat = "XML"
    keywordsDBname = "keywords_xml"

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
