# coding = utf-8
# -*- coding: utf-8 -*-

from src.soilpulse.resource_management import DatasetHandler, DatasetHandlerFactory, Pointer, Crawler

class MySQLDataset(DatasetHandler):
    datasetFormat = "MySQL"
    def __init__(self, name, doi = None):
        super(MySQLDataset, self).__init__(name, doi)
        self.databaseName = None
        self.tables = []
        self.foreignKeys = []

    def showContents(self):
        pass
DatasetHandlerFactory.registerDatasetType(MySQLDataset, "mysql")

class MySQLPointer(Pointer):
    pass

class MySQLcrawler(Crawler):
    pass