# -*- coding: utf-8 -*-
"""
@author: Jan Devátý
"""

class Crawler:
    """
    Top level abstract class of the crawler metadata/data crawler
    """
    resourcePath = None
    def __init__(self):
        pass

    def getMetadataStructure(self):
        """
        Parses the source and translate it to metadata elements structure
        :return:
        """

class FilesystemCrawler(Crawler):
    """
    Crawler for file system repositories
    """
    # list of all the directories that will be crawled through
    directories = []
    # list of all the files that will be crawled through
    files = []
    pass

class XMLcrawler(Crawler):
    pass

class HTMLcrawler(Crawler):
    pass

class MySQLcrawler(Crawler):
    pass