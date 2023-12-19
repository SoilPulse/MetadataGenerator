# -*- coding: utf-8 -*-
"""
@author: Jan Devátý
"""

class Crawler:
    """
    Top level abstract class of the crawler metadata/data crawler
    """

    def __init__(self, resurceURI):
        self.resourceURI = resurceURI
        pass

    def getMetadataStructure(self):
        """
        Parses the source and translate it to metadata elements structure
        :return:
        """
        return

class FilesystemCrawler(Crawler):
    """
    Crawler for file system repositories
    """

    pass

class XMLcrawler(Crawler):
    pass

class HTMLcrawler(Crawler):
    pass

class MySQLcrawler(Crawler):
    pass