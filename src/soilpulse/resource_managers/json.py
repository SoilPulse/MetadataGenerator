# coding = utf-8
# -*- coding: utf-8 -*-

import json

from src.soilpulse.resource_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler
from src.soilpulse.db_access import EntityKeywordsDB
# just for the standalone functions - will be changed
from src.soilpulse.resource_management import *


class JSONContainer(ContainerHandler):
    containerType = 'json'
    containerFormat = "JSON"
    keywordsDBname = "keywords_json"

    def __init__(self, name, content, path = None):
        super(JSONContainer, self).__init__(name)
        # the JSON content
        self.content = content
        self.path = path

    def showContents(self, depth = 0, ind = ". "):
        """
        Prints basic info about the container and invokes showContents on all of its containers

        :param depth: current depth of showKeyValueStructure recursion
        :param ind: string of a single level indentation
        """
        t = ind * depth

        print("{}{} - {} ({}) [{}]".format(t, self.id, self.name, self.containerType, len(self.containers)))
        self.showKeyValueStructure(self.content, t, 0)
        if self.containers:
            depth += 1
            for cont in self.containers:
                cont.showContents(depth)
        return
    def showKeyValueStructure(self, json, t = "", depth = 0, depthLimit = 0, ind = ".", sep = ">"):
        """
        Prints out the structure of JSON container recursively
        Each level is indented by 'depth times ind' character sequence
        The indentation allways starts with a single separator 'sep'

        :param json: the json structure to be shown
        :param t: the indentation from previous level of container
        :param depth: current depth of showKeyValueStructure recursion
        :param depthLimit: maximum depth of recursion to go to
        :param ind: string of a single level indentation
        :param sep: outer/inner indentation separator (outer is indentation from previous level of container, inner is within the JSON)

        :return: nothing
        """
        if depthLimit == 0 or depth < depthLimit:
            tt = ind * depth
            if isinstance(json, dict):
                for k, v in json.items():
                    if isinstance(v, dict):
                        if not json == {}:
                            print(f"{t}{sep}{tt}{k}:")
                            depth += 1
                            self.showKeyValueStructure(v, t, depth, depthLimit)
                        else:
                            print(f"{t}{sep}{tt}{k}: {{}}")
                    elif isinstance(v, list):
                        if len(v) == 0:
                            print(f"{t}{sep}{tt}{k}: []")
                        elif len(v) == 1:
                            if not isinstance(v, (dict, list)):
                                print(f"{t}{sep}{tt}{k}: {v}")
                            else:
                                print(f"{t}{sep}{tt}{k}:")
                                depth += 1
                                self.showKeyValueStructure(v, t, depth, depthLimit)
                    else:
                        print(f"{t}{sep}{tt}{k}: {v}")

            elif isinstance(json, list):
                depth += 1
                i = 0
                for v in json:
                    if isinstance(v, (dict, list)):
                        print(f"{t}{sep}{tt}{i}:")
                        depth += 1
                        self.showKeyValueStructure(v, t, depth, depthLimit)
                    else:
                        print(f"{t}{sep}{tt}{i}: {v}")
                    i += 1
        return

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
