# coding = utf-8
# -*- coding: utf-8 -*-

import os
import pandas
import frictionless

from ..project_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler

class TableContainer(ContainerHandler):
    containerType = 'table'
    containerFormat = "Table"

    # dictionary of DB fields needed to save this subclass instance attributes
    DBfields = {}
    # DBfields = {"line_delimiter": "text",
    #             "cell_delimiter": "datetime",
    #             "decimal_separator": "datetime",
    #             "encoding": "text"}

    serializationDict = {}
    # serializationDict = {"line_delimiter": "lineDelimiter",
    #                      "cell_delimiter": "cellDelimiter",
    #                      "decimal_separator": "decimalSeparator"}

    def __init__(self, project_manager, parent_container, **kwargs):
    # dictionary of attribute names to be used for DB save/update - current values need to be obtained at right time before saving
        super().__init__(project_manager, parent_container, **kwargs)
        # self.lineDelimiter = kwargs.get("line_delimiter")
        # self.cellDelimiter = kwargs.get("cell_delimiter")
        # self.decimalSeparator = kwargs.get("decimal_separator")
        self.fl_resource = kwargs.get("fl_resource")
        self.pd_dataframe = kwargs.get("pd_dataframe")

        self.crawler = TableCrawler(self)

        pass

    def getCrawled(self, cascade=True):
        """
        Executes the routines for scanning, recognizing and extracting metadata (and maybe data)
        """
        if self.crawler:
            columns = self.crawler.crawl()
            if columns:
                # print(f"tables:\n{tables}")
                # print("\n\n")
                self.containers = columns
            # print(f"table cont {self.id} containers: {self.containers}")

        if cascade:
            for container in self.containers:
                container.getCrawled(cascade)
        return

ContainerHandlerFactory.registerContainerType(TableContainer, TableContainer.containerType)

class TableCrawler(Crawler):
    """
    Crawler for table structures
    """
    crawlerType = "table structure crawler"

    def __init__(self, container):
        super().__init__(container)

        # print(f"Table crawler created for container #{self.container.id} '{self.container.name}'")

    def crawl(self, forceRecrawl=False, report=True):
        """
        Do the crawl - go through the file and detect defined elements

        :param forceRecrawl: whether to crawl a container eventhough it was already crawled
        :return: list of table containers
        """

        if not self.container.wasCrawled or (not self.container.wasCrawled and forceRecrawl):

            print(f"crawling table '{self.container.name}' container #{self.container.id}") if report else None
            #
            column_conts = []
            # print(self.container.fl_resource.schema)
            for field in self.container.fl_resource.schema.fields:
                cont_args = {"name": field.name, "data_type": field.type}
                print(cont_args)
                # create new container from found TableResources
                column_conts.append(
                    self.container.project.containerFactory.createHandler("column", self.container.project,
                                                                          self.container, **cont_args))
            # change flag of parent container
            self.container.wasCrawled = True
            return column_conts
        else:
            print(f"Container {self.container.id} was already crawled.")
            return None

class ColumnContainer(ContainerHandler):
    containerType = 'column'
    containerFormat = "Table column"

    serializationDict = {"data_type": "dataType"}
    def __init__(self, project_manager, parent_container, **kwargs):
        super().__init__(project_manager, parent_container, **kwargs)
        self.dataType = kwargs.get("data_type")
        self.unit = kwargs.get("unit")
        self.method = kwargs.get("method")
        pass

ContainerHandlerFactory.registerContainerType(ColumnContainer, ColumnContainer.containerType)