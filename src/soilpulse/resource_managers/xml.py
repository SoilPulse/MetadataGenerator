# coding = utf-8
# -*- coding: utf-8 -*-

from src.soilpulse.resource_management import DatasetHandler, DatasetHandlerFactory, Pointer, Crawler

class XMLDataset(DatasetHandler):
    datasetType = 'xml'
    datasetFormat = "XML"
    def __init__(self, name, doi = None):
        super(XMLDataset, self).__init__(name, doi)

    def showContents(self):
        pass

DatasetHandlerFactory.registerDatasetType(XMLDataset, XMLDataset.datasetType)

class XMLPointer(Pointer):
    pass

class XMLcrawler(Crawler):
    pass
