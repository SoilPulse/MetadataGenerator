# coding = utf-8
# -*- coding: utf-8 -*-

from frictionless import Field, system, steps
import time

from ..project_management import ContainerHandler, ContainerHandlerFactory, Crawler, CrawlerFactory
import json


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
        self.primary_key_container = None
        self.fl_resource = kwargs.get("fl_resource")
        self.steps = []
        self.fl_resource_trans = None

        self.pd_dataframe = kwargs.get("pd_dataframe")

        self.crawler = TableCrawler(self)

        pass

    def getAnalyzed(self, cascade=True, force=False, report=False):
        """
        Induces further decomposition of the table container into column containers.
        """
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
        Induces content search for metadata elements based on appropriate set of search rules and terms.
        """
        if super().getCrawled(cascade, force):
            if self.crawler:
                self.crawler.crawl(report)

            if cascade:
                for container in self.containers:
                    container.getCrawled(cascade, force, report)
        return

    def get_frictionless_resource(self):
        """
        Compose and update the frictionless Resource definition based on column sub-containers.
        Incorporates concepts, methods & units to fields scheme
        """

        fields = []
        for cont in self.containers:
            # procedure valid for column containers only
            if isinstance(cont, ColumnContainer):
                # extract list of uris from container's concepts
                concepts = []
                for str, concs in cont.concepts.items():
                    for conc in concs:
                        concepts.append(conc["uri"])
                # extract list of uris from container's methods
                methods = []
                for str, meths in cont.methods.items():
                    for meth in meths:
                        methods.append(meth["uri"])
                # extract list of uris from container's units
                units = []
                for str, unts in cont.units.items():
                    for unt in unts:
                        units.append(unt["uri"])
                descriptor = {
                    "name": cont.name,
                    "type": cont.dataType,
                    "concepts": concepts,
                    "methods": methods,
                    "units": units
                }
                fields.append(descriptor)

        # create list of Field objects and replace the schema fields
        self.fl_resource.schema.fields = [Field.from_descriptor(descriptor) for descriptor in fields]
        if self.primary_key_container:
            self.fl_resource.scema.primaryKey = self.primary_key_container.name
        return self.fl_resource

    def load_transformation_steps_from_file(self, path):
        """
        Loads a file content and tries to evaluate it as a steps definition for transformation Pipeline
        """
        with open(path, 'r') as f:
            self.steps = eval(f.read())
        print(f"loaded transformation steps for table container {self.name}:\n {self.steps}")
        return

    def set_transformation_steps(self, steps_json):
        """Set the transformation steps from a JSON string or dictionary."""
        if isinstance(steps_json, str):
            self.steps = json.loads(steps_json)
        elif isinstance(steps_json, list):
            self.steps = steps_json
        else:
            raise ValueError("Steps must be a JSON string or list of dictionaries.")
        print(f"loaded transformation steps for table container {self.name}:\n {self.steps}")
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
        """
        Creates column sub-containers for the table
        """
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
        self.foreignKeys = None

        pass

    def getAnalyzed(self, cascade=True, force=False, report=False):
        """
        Induces further decomposition of the table container into column containers.
        """
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

    def get_frictionless_field(self):
       # return EnrichedField(
       #      name=self.name,
       #      field_type=self.dataType,
       #      concepts=self.concepts,
       #      methods=self.methods,
       #      units=self.units,
       #  )
        descriptor = {"name": self.name, "type": self.dataType}
        descriptor["concepts"] = self.concepts or []
        descriptor["methods"] = self.methods or []
        descriptor["units"] = self.units or []
        return Field.from_descriptor(descriptor)


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
        print(f"crawling column '{self.container.name}' of container #{self.container.id}") if report else None

        # search for string to concept translations in project dictionary
        start_time = time.time()
        # print(f"searching '{self.container.name}' for string-concept translations in project's dictionary")
        all_translations = self.find_translations_in_dictionary(self.container.project.conceptsTranslations, full_match_only=False)
        for translation in all_translations:
            for string, concepts in translation.items():
                for concept in concepts:
                    self.container.addStringConcept(string, concept)
        # search for string to method translations in project dictionary
        # print(f"searching '{self.container.name}' for string-method translations in project's dictionary")
        all_translations = self.find_translations_in_dictionary(self.container.project.methodsTranslations, full_match_only=False)
        for translation in all_translations:
            for string, methods in translation.items():
                for method in methods:
                    self.container.addStringMethod(string, method)
        # search for string to unit translations in project dictionary
        # print(f"searching '{self.container.name}' for string-unit translations in project's dictionary")
        all_translations = self.find_translations_in_dictionary(self.container.project.unitsTranslations, full_match_only=False)
        for translation in all_translations:
            for string, units in translation.items():
                for unit in units:
                    self.container.addStringUnit(string, unit)
        execution_time = time.time() - start_time
        # print(f"\texecution time: {execution_time:.3f} seconds\n")

        # search for string to concept translations in all registered global concept vocabularies
        start_time = time.time()
        all_translations = []
        # print(f"searching vocabularies for string-concept translations of '{self.container.name}'")
        for vocab in self.container.project.globalConceptsVocabularies.values():
            all_translations.extend(self.find_translations_in_vocabulary(vocab, full_match_only=True))
        for translation in all_translations:
            for string, concepts in translation.items():
                for concept in concepts:
                    self.container.addStringConcept(string, concept)
        # search for string to method translations
        all_translations = []
        # print(f"searching vocabularies for string-method translations of '{self.container.name}'")
        for vocab in self.container.project.globalMethodsVocabularies.values():
            all_translations.extend(self.find_translations_in_vocabulary(vocab, full_match_only=True))
        for translation in all_translations:
            for string, methods in translation.items():
                for method in methods:
                    self.container.addStringMethod(string, method)
        # search for string to unit translations
        found_units = []
        # print(f"searching vocabularies for string-unit translations of '{self.container.name}'")
        for vocab in self.container.project.globalUnitsVocabularies.values():
            found_units.extend(self.find_translations_in_vocabulary(vocab, full_match_only=True))
        for translation in all_translations:
            for string, units in translation.items():
                for unit in units:
                    self.container.addStringUnit(string, unit)

        execution_time = time.time() - start_time
        # print(f"\texecution time: {execution_time:.3f} seconds")

        # change flag of parent container
        self.container.wasCrawled = True
        return

CrawlerFactory.registerCrawlerType(ColumnCrawler)

#
# class EnrichedField(Field):
#     def __init__(self, name, field_type="any", concepts=None, methods=None, units=None, **kwargs):
#         # Construct descriptor with standard and custom attributes
#         descriptor = {"name": name, "type": field_type, **kwargs}
#         if concepts is not None:
#             descriptor["concepts"] = concepts
#         if methods is not None:
#             descriptor["methods"] = methods
#         if units is not None:
#             descriptor["units"] = units
#
#         # Pass descriptor to the parent class
#         super().__init__(name=name)
#
# # replace frictionless default Field class with EnrichedField class
# def custom_field_factory(descriptor):
#     return EnrichedField(descriptor)
# # register the custom field factory globally
# system.create_field = custom_field_factory