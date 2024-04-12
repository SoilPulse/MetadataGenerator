# coding = utf-8
# -*- coding: utf-8 -*-

from ..resource_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler
from ..db_access import EntityKeywordsDB


class MySQLContainer(ContainerHandler):
    containerType = 'mysql'
    containerFormat = "MySQL"
    keywordsDBname = "keywords_mysql"

    def __init__(self, name):
        super(MySQLContainer, self).__init__(name)
        self.databaseName = None
        self.tables = []
        self.foreignKeys = []


    def showContents(self):
        pass

ContainerHandlerFactory.registerContainerType(MySQLContainer, MySQLContainer.containerType)
EntityKeywordsDB.registerKeywordsDB(MySQLContainer.containerType, MySQLContainer.keywordsDBname)

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