# coding = utf-8
# -*- coding: utf-8 -*-

import os
import pandas
import frictionless

from ..project_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler, CrawlerFactory

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

    def getAnalyzed(self, cascade, force=False, report=False):
        if super().getAnalyzed(cascade, force):
            if self.crawler:
                columns = self.crawler.analyze(report)
                if columns:
                    # print(f"tables:\n{tables}")
                    # print("\n\n")
                    self.containers = columns
                # print(f"table cont {self.id} containers: {self.containers}")

            if cascade:
                for container in self.containers:
                    container.getAnalyzed(cascade, force, report)
            self.wasAnalyzed = True
        return

    def getCrawled(self, cascade=True, force=False, report=False):
        """
        Executes the routines for scanning, recognizing and extracting metadata (and maybe data)
        """
        if super().getCrawled(cascade, force):
            if self.crawler:
                self.crawler.crawl(report)

            if cascade:
                for container in self.containers:
                    container.getCrawled(cascade, force, report)
        return

    def getFrictionlessResource(self):
        return

ContainerHandlerFactory.registerContainerType(TableContainer, TableContainer.containerType)

class TableCrawler(Crawler):
    """
    Crawler for table structures
    """
    crawlerType = "table"

    def __init__(self, container):
        super().__init__(container)

        # print(f"Table crawler created for container #{self.container.id} '{self.container.name}'")

    def analyze(self, report=True):
        print(f"\tanalyzing table '{self.container.name}' container #{self.container.id}") if report else None
        #
        column_conts = []
        # print(self.container.fl_resource.schema)
        # try:
        for field in self.container.fl_resource.schema.fields:
            cont_args = {"name": field.name, "data_type": field.type}
            # print(cont_args)
            # create new container from found TableResources
            new_column = self.container.project.containerFactory.createHandler("column", self.container.project,
                                                                      self.container, **cont_args)
            column_conts.append(new_column)
        # except:
        #     print(self.container.fl_resource)
        # print(f"\t\tfound {len(column_conts)} columns")
        # change flag of parent container
        self.container.wasAnalyzed = True
        return column_conts

    def crawl(self, report=True):
        """
        Do the crawl - go through the container and detect defined elements
        The results of the crawl are directly assigned to crawler's parent container attributes

        :return:
        """

        print(f"no crawling procedure defined for table crawler") if report else None
        # change flag of parent container
        self.container.wasCrawled = True
        return

CrawlerFactory.registerCrawlerType(TableCrawler)


class ColumnContainer(ContainerHandler):
    containerType = 'column'
    containerFormat = "Table column"

    serializationDict = {"data_type": "dataType"}

    def __init__(self, project_manager, parent_container, **kwargs):
        super().__init__(project_manager, parent_container, **kwargs)
        self.dataType = kwargs.get("data_type")
        self.crawler = ColumnCrawler(self)

        pass

    def getAnalyzed(self, cascade=True, force=False, report=False):
        if super().getAnalyzed(cascade, force):
            if self.crawler:
                self.crawler.analyze(report)

            if cascade:
                for container in self.containers:
                    container.getAnalyzed(cascade, force, report)
            self.wasAnalyzed = True
        return

    def getCrawled(self, cascade=True, force=False, report=False):
        """
        Executes the routines for scanning, recognizing and extracting metadata (and maybe data)
        """

        if super().getCrawled(cascade, force):
            if self.crawler:
                self.crawler.crawl(report)

            if cascade:
                for container in self.containers:
                    container.getCrawled(cascade, force, report)
        return

ContainerHandlerFactory.registerContainerType(ColumnContainer, ColumnContainer.containerType)

class ColumnCrawler(Crawler):
    """
    Crawler for table columns
    """
    crawlerType = "column"

    def __init__(self, container):
        super().__init__(container)

        # print(f"Column crawler created for container #{self.container.id} '{self.container.name}'")

    def analyze(self, report=True):
        print(f"\tno analysis procedure defined for column container") if report else None
        # change flag of parent container
        self.container.wasAnalyzed = True
        return None

    def crawl(self, report=True):
        """
        Do the crawl - go through the container and detect defined elements
        The results of the crawl are directly assigned to crawler's parent container attributes

        :return:
        """

        print(
            f"crawling column '{self.container.name}' of container #{self.container.id}") if report else None
        # search for string to concept translations
        self.container.concepts = self.find_translations(self.container.project.globalConceptsVocabulary)
        # print(f"\tfound concept translations:\n\t{self.container.concepts}") if len(self.container.concepts) > 0 else None
        # search for string to method translations
        self.container.methods = self.find_translations(self.container.project.globalMethodsVocabulary)
        # print(f"\tfound methods translations:\n\t{self.container.methods}") if len(self.container.methods) > 0 else None
        # search for string to unit translations
        self.container.units = self.find_translations(self.container.project.globalUnitsVocabulary)
        # print(f"\tfound units translations:\n\t{self.container.units}") if len(self.container.units) > 0 else None

        # change flag of parent container
        self.container.wasCrawled = True
        return

CrawlerFactory.registerCrawlerType(TableCrawler)