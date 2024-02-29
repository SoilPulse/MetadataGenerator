# coding = utf-8
# -*- coding: utf-8 -*-

from src.soilpulse.resource_management import DatasetHandler, DatasetHandlerFactory, Pointer, Crawler

class MySQLDataset(DatasetHandler):
    datasetType = 'mysql'
    datasetFormat = "MySQL"
    def __init__(self, name, doi = None):
        super(MySQLDataset, self).__init__(name, doi)
        self.databaseName = None
        self.tables = []
        self.foreignKeys = []

    def showContents(self):
        pass
DatasetHandlerFactory.registerDatasetType(MySQLDataset, MySQLDataset.datasetType)

class MySQLPointer(Pointer):
    def __init__(self, tableName, indexColumnName, indexValue, valueColumnName, startChar = None, numChars = None):
        # name of the table where the value is stored
        self.tableName = tableName
        # name of the column with index by which the row with value can be found
        self.indexColumnName = indexColumnName
        # index value of the row
        self.indexValue = indexValue
        # name of the column where the value is stored
        self.valueColumnName = valueColumnName
        # optionally start character of the value
        self.startChar = startChar
        # optionally number of characters the value takes
        self.numChars = numChars
    pass

class MySQLcrawler(Crawler):
    pass