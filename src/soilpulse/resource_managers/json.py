# coding = utf-8
# -*- coding: utf-8 -*-

import json
import os

from ..project_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler
from ..db_access import EntityKeywordsDB
# just for the standalone functions - will be changed
# from ..resource_management import *


class JSONContainer(ContainerHandler):
    containerType = 'json'
    containerFormat = "JSON"
    keywordsDBname = "keywords_json"

    # dictionary of DB fields needed to save this subclass instance attributes
    DBfields = {"relative_path": ["text", 255], "content": ["text", 2047]}

    def __init__(self, project_manager, parent_container, **kwargs):
        super(JSONContainer, self).__init__(project_manager, parent_container, **kwargs)
        # the JSON content
        self.content = kwargs["content"]
        self.path = kwargs["path"]
        self.rel_path = self.path.replace(project_manager.temp_dir, "") if self.path is not None else None

        self.crawler = JSONcrawler(self)

        self.serializationDict = {"relative_path": "rel_path", "content": "content"}

    def showContents(self, depth = 0, ind = ". "):
        """
        Prints basic info about the container and invokes showContents on all of its containers

        :param depth: current depth of showKeyValueStructure recursion
        :param ind: string used for one level of indentation
        """
        t = ind * depth

        print(f"{t}{self.id} - {self.name} ({self.containerType}) [{len(self.containers)}]")
        # self.showKeyValueStructure(self.content, t, 0)
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
        :param ind: string used for one level of indentation
        :param sep: outer/inner indentation separator (outer is indentation from previous level of container, inner is within the JSON)

        :return: nothing
        """
        if depthLimit == 0 or depth < depthLimit:
            tt = ind * depth
            depth += 1
            # if the currently passed json is a dictionary
            if isinstance(json, dict):
                if len(json) == 0:
                    print(f"{t}{sep}{tt}{json}: {{}}")
                else:
                    for k, v in json.items():
                        if isinstance(v, dict):
                            if len(v) == 0:
                                print(f"{t}{sep}{tt}{k}: {{}}")
                            else:
                                print(f"{t}{sep}{tt}{k}:")
                                self.showKeyValueStructure(v, t, depth, depthLimit)
                        elif isinstance(v, list):
                            if len(v) == 0:
                                #
                                print(f"{t}{sep}{tt}{k}: []")
                            else:
                                print(f"{t}{sep}{tt}{k}:")
                                self.showKeyValueStructure(v, t, depth, depthLimit)
                        else:
                            print(f"{t}{sep}{tt}{k}: {v}")

            elif isinstance(json, list):
                if len(json) == 0:
                    print(f"{t}{sep}{tt}: []")
                else:
                    i = 0
                    for v in json:
                        if len(v) == 0:
                            print(f"{t}{sep}{tt}{i}: []")
                        else:
                            print(f"{t}{sep}{tt}{i}:")
                            self.showKeyValueStructure(v, t, depth, depthLimit)
                        i += 1
            else:
                print(f"{t}{sep}{tt}: {json}")

        return

    def saveAsFile(self, dir, filename):

        fullpath = os.path.join(dir, filename)
        self.path = fullpath
        self.project.containersOfPaths.update({self.path: self.id})
        return fullpath

    def getCrawled(self):
        self.crawler.crawl()
        pass

ContainerHandlerFactory.registerContainerType(JSONContainer, JSONContainer.containerType)
EntityKeywordsDB.registerKeywordsDB(JSONContainer.containerType, JSONContainer.keywordsDBname)

class JSONPointer(Pointer):

    pointerType = type

    def __init__(self, filename, startChar, numChars):

        pass


class JSONcrawler(Crawler):
    """
    Crawler for file system repositories
    """

    crawlerType = "JSON crawler"

    def __init__(self, container):
        self.container = container
        # print(f"\tJSON crawler created for container #{self.container.id} '{self.container.name}' (file '{self.container.path}')")
        pass

    def crawl(self):
        print("No crawling procedure defined yet for JSON crawler")
        pass
