# -*- coding: utf-8 -*-
"""
@author: Jan Devátý
"""


from .exceptions import MetadataSchemeException

class MetadataStructureMap:
    """
    Realisation of a metadata element set and relationships describing particular dataset
    """
    def __init__(self):
        # list of all metadata entities and their locator in the structure map [[MetadataEntity, Pointer], ...]
        self.elements = []
        # entity factory for this MetadataStructureMap
        self.entityFactory = EntityManager()

        return

    def addEntity(self, entity, pointer):
        """
        Adds an entity-pointer pair to elements list

        :param entity: MetadataEntity instance
        :param pointer: Pointer instance
        """
        self.elements.append([entity, pointer])
        return

    def removeEntity(self, index):
        """
        Removes an entity-pointer pair from elements list by index

        :param index: list index of the entity-pointer pair to be removed
        """
        del self.elements[index]

    def mergeEntities(self):
        """
        Merges two entities into one.

        """
        return

    def splitEntity(self):
        """
        Splits one entity into two
        """

    def saveToDatabase(self):
        """
        Saves the structure map to a database
        """
        return

    def checkConsistency(self):
        """
        Checks the number of appearances of entity types
        """
        # self.entityFactory.checkMinCounts()
        # self.entityFactory.checkMaxCounts()

        print("Minimum count check results:")
        for entity in self.entityFactory.checkMinCounts():
            if entity[2] < entity[1]:
                print("\tmissing element type '{}' (minimum count {}, current count {})".format(entity[0], entity[1],
                                                                                                entity[2]))

        print("")

        print("Maximum count check results:")
        for entity in self.entityFactory.checkMaxCounts():
            if entity[2] > entity[1]:
                print(
                    "\ttoo many elements of type '{}' (maximum count {}, current count {})".format(entity[0], entity[1],
                                                                                                   entity[2]))

        return

class EntityManager:
    """
    Manages the entity type classes, provides access to entity instances, takes care about limiting number of instances of a particular type
    """

    # directory of registered entity classes
    metadataEntities = {}
    # minimum number of instances per dataset
    minCounts = {}
    # maximum number of instances per dataset
    maxCounts = {}
    # current count of instances
    currentCount = {}
    #
    keywordMapping = {}

    _instance = None
    def __init__(self):
        return

    @classmethod
    def registerMetadataEntityType(cls, entityClass):
        cls.metadataEntities[entityClass.key] = entityClass
        cls.minCounts[entityClass.key] = entityClass.minMultiplicity
        cls.maxCounts[entityClass.key] = entityClass.maxMultiplicity
        cls.currentCount[entityClass.key] = 0
        for kw in entityClass.keywords:
            cls.keywordMapping.update({kw: entityClass.key})
        return

    @classmethod
    def createEntityInstance(cls, entityType, *args):
        if entityType not in cls.metadataEntities.keys():
            raise ValueError("Unsupported metadata entity type '{}'".format(entityType))
        else:
            #print("entity type requested: {}\nmax count: {}\ncurrent count: {}".format(entityType, cls.maxCounts[entityType], cls.currentCount[entityType]))
            cls.currentCount[entityType] += 1
            return cls.metadataEntities[entityType](*args)

    @classmethod
    def checkMinCounts(cls):
        elementCounts = []
        for entityType, entityClass in cls.metadataEntities.items():
            if cls.currentCount[entityType] < entityClass.minMultiplicity:
                elementCounts.append([entityClass.name, cls.minCounts[entityType], cls.currentCount[entityType]])

        return elementCounts

    @classmethod
    def checkMaxCounts(cls):
        elementCounts = []
        for entityType, entityClass in cls.metadataEntities.items():
            if entityClass.maxMultiplicity is not None:
                if cls.currentCount[entityType] > entityClass.maxMultiplicity:
                    elementCounts.append([entityClass.name, cls.maxCounts[entityType], cls.currentCount[entityType]])
        return elementCounts
    @classmethod
    def showKeywordsMapping(cls):
        print("\nkeywords mapping:")
        for k,v in cls.keywordMapping.items():
            print("{}: {}".format(k,v))

    @classmethod
    def showEntityCount(cls):
        print("\ncurrent entity count:")
        for k,v in cls.currentCount.items():
            print("{}: {}".format(k,v))

class MetadataEntity:
    """
    Top level abstract class of the metadata entity. Defines metadata elements interface
    """

    # entity ID in metadata scheme
    ID = None
    # entity id string
    key = None
    # entity name
    name = None
    # description of the entity (= definition in BonaRes scheme)
    description = None
    # lowest number of appearances in resource, also works as optional/mandatory indicator
    minMultiplicity = 0
    # highest number of appearances in resource (None meaning infinity)
    maxMultiplicity = None
    # ? class of the super-element
    subtypeOf = None
    # ? data type that the element can be
    dataType = None
    # ? value domain the element can have
    domain = None
    # list of keywords used for identification of the element in the data resource
    keywords = None

    def __init__(self, value):
        # the actual value of the metadata element instance
        self.value = value
        # list of child metadata elements
        self.childElements = []
        # the parent element of self
        self.parentElement = None
        return

    def getXMLrepresenatation(self):
        """
        Creates the string of element's XML representation
        :return: XML string
        """
        pass

    def getMySQLrepresenatation(self):
        """
        Creates the string of element's MySQL snippet
        :return: MySQL query string
        """

        pass

class TextMetadataEntity(MetadataEntity):
    """
    Abstract interface class of metadata element with textual value
    """

    def __init__(self, value, language, encoding):
        # the actual value of the metadata element
        super(TextMetadataEntity, self).__init__(value)
        # the original language of the element value
        self.language = language
        # the encoding of the value
        self.encoding = encoding
        # translations of the element value in different languages
        self.translations = {}
        return

class DateMetadataEntity(MetadataEntity):
    """
    Abstract interface class of metadata element with date value
    """

    def __init__(self, value):
        # the actual value of the metadata element
        super(DateMetadataEntity, self).__init__(value)
        return

class GeographicalMetadataEntity(MetadataEntity):
    """
    Abstract interface of metadata element with geographical value
    """
    def __init__(self, coordinateSystem, epsg = None):
        # the coordinate system of the element
        self.coordinateReferenceSystem = coordinateSystem
        # the EPSG code of the coordinate system of the element
        self.EPSGcode = epsg

class RoleMetadataEntity(MetadataEntity):
    """
    Abstract interface class of metadata element with role value
    """

    def __init__(self, value):
        # the actual value of the metadata element
        super(RoleMetadataEntity, self).__init__(value)
        return

class Title(TextMetadataEntity):
    ID = "1"
    key = "title"
    name = "Title"
    description = "A characteristic, unique name by which the dataset is known."
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["title", "<h1>"]

    def __str__(self):
        return "metadata entity 'Title'"

EntityManager.registerMetadataEntityType(Title)

class AlternateTitle(TextMetadataEntity):
    ID = "2"
    key = "alternate_title"
    name = "Alternate title"
    description = "A short name by which the dataset is also known."
    minMultiplicity = 0
    maxMultiplicity = None
    keywords = ["<h2>"]
EntityManager.registerMetadataEntityType(AlternateTitle)

class Summary(TextMetadataEntity):
    ID = "3"
    key = "summary"
    name = "Summary"
    description = "Brief narrative summary of the content of the dataset."
    minMultiplicity = 1
    maxMultiplicity = None
    keywords = ["<h2>", "description"]
EntityManager.registerMetadataEntityType(Summary)

class GraphicOverview(MetadataEntity):
    ID = "4"
    key = "graphic_overview"
    name = "Graphic overview"
    description = "Graphic that provides an illustration of the dataset."
    minMultiplicity = 0
    maxMultiplicity = None
    keywords = ["scheme"]
EntityManager.registerMetadataEntityType(GraphicOverview)

# replaced by DateMetadataEntity superclass
# class Date(MetadataEntity):
#     ID = "5"
#     key = "date"
#     name = "Date"
#     description = "The date when the dataset was or will be made ..."
#     minMultiplicity = 4
#     maxMultiplicity = None
#     keywords = ["date"]
# EntityManager.registerMetadataEntityType(Date)

class DateAccapted(DateMetadataEntity):
    ID = "5.1"
    key = "date_accepted"
    name = "Date accepted"
    description = "The date that the publisher accepted the resource into their system."
    # subtypeOf = Date
    minMultiplicity = 0
    maxMultiplicity = 1
    keywords = ["accapted"]
EntityManager.registerMetadataEntityType(DateAccapted)

class DateAvailable(DateMetadataEntity):
    ID = "5.2"
    key = "date_available"
    name = "Date available"
    description = "The date the resource was or will be made publicly available."
    # subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["available"]
EntityManager.registerMetadataEntityType(DateAvailable)

class DateCollected(DateMetadataEntity):
    ID = "5.3"
    key = "date_collected"
    name = "Date collected"
    description = "The date or date range in which the dataset content was collected."
    # subtypeOf = Date
    minMultiplicity = 0
    maxMultiplicity = 2
    keywords = ["collected"]
EntityManager.registerMetadataEntityType(DateCollected)

class DateCopyrighted(DateMetadataEntity):
    ID = "5.4"
    key = "date_copyrighted"
    name = "Date copyrighted"
    description = "The specific, documented date at which the dataset receives a copyrighted status, if applicable."
    # subtypeOf = Date
    minMultiplicity = 0
    maxMultiplicity = 1
    keywords = ["copyrighted", "copyright"]
EntityManager.registerMetadataEntityType(DateCopyrighted)

class DateCreated(DateMetadataEntity):
    ID = "5.5"
    key = "date_created"
    name = "Date created"
    description = "The date the dataset itself was put together; a single date for a final component (e.g. the finalised file with all of the data)."
    # subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["created"]
EntityManager.registerMetadataEntityType(DateCreated)

class DateIssued(DateMetadataEntity):
    ID = "5.6"
    key = "date_issued"
    name = "Date issued"
    description = "The date that the dataset is published or distributed to the data centre."
    # subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["issued"]
EntityManager.registerMetadataEntityType(DateIssued)

class DateSubmitted(DateMetadataEntity):
    ID = "5.7"
    key = "date_submitted"
    name = "Date submitted"
    description = "The date the author submits the resource to the publisher. This could be different from “Accepted” if the publisher then applies a selection process."
    # subtypeOf = Date
    minMultiplicity = 0
    maxMultiplicity = 1
    keywords = ["submitted"]
EntityManager.registerMetadataEntityType(DateSubmitted)

class DateUpdated(DateMetadataEntity):
    ID = "5.7"
    key = "date_updated"
    name = "Date updated"
    description = "The date of the last update (last revision) to the dataset, when the dataset is being added to."
    # subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["updated", "update", "revised", "revision"]
EntityManager.registerMetadataEntityType(DateUpdated)

class DateValid(DateMetadataEntity):
    ID = "5.8"
    key = "date_valid"
    name = "Date valid"
    description = "The date or date range during which the dataset or resource is accurate."
    # subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["valid", "valid until"]
EntityManager.registerMetadataEntityType(DateValid)

class GeographicalBoundingBox(GeographicalMetadataEntity):
    ID = "9"
    key = "bounding_box"
    name = "Geographical bounding box"
    description = "The spatial limits of a box. A box is defined by two geographic points.\
    Lower left corner and upper right corner. Each point is defined by its longitude and latitude value."
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["bounding box", "extent", "geographical", "covers", "geoLocations"]

    def __init__(self, northLat, southLat, westLong, eastLong, coordinateSystem, epsg = None):
        super(GeographicalBoundingBox, self).__init__(coordinateSystem, epsg)
        self.nortLatitude = northLat
        self.southLatitude = southLat
        self.westLongitude = westLong
        self.eastLongitude = eastLong
        return
EntityManager.registerMetadataEntityType(GeographicalBoundingBox)

class TemporalExtent(DateMetadataEntity):
    ID = "11"
    key = "temporal_extent"
    name = "Temporal extent"
    description = "The time period in which the resource content was collected (e.g. From 2008-01-01 to 2008-12-31)"
    minMultiplicity = 0
    maxMultiplicity = 1
    keywords = ["temporal extent"]

EntityManager.registerMetadataEntityType(TemporalExtent)
