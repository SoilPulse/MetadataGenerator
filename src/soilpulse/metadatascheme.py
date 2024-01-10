# -*- coding: utf-8 -*-
"""
@author: Jan Devátý
"""


from .exceptions import MetadataSchemeException

class MetadataStructureMap:
    def __init__(self):
        self.elements = []
    pass

class EntityManager:
    """
    Manages the entity type classes, provides access to entity instances, takes care about limiting number of instances of a particular type
    """

    # directory of various entity classes
    metadataEntities = {}
    # minimum number of instances per dataset
    minCounts = {}
    # maximum number of instances per dataset
    maxCounts = {}
    # current count of instances
    currentCount = {}

    _instance = None
    def __init__(self):
        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance

    @classmethod
    def registerMetadataEntityType(cls, entityType, minCount, maxCount):
        def decorator(entityClass):
            cls.metadataEntities[entityType] = entityClass
            cls.minCounts[entityType] = minCount
            cls.maxCounts[entityType] = maxCount
            cls.currentCount[entityType] = 0
            return entityClass

        return decorator

    @classmethod
    def createEntityInstance(cls, entityType, params):
        if entityType not in cls.metadataEntities:
            raise ValueError("Unsupported metadata entity type '{}'".format(entityType))
        else:
            # for entity types with unlimited multiplicity
            if cls.maxCounts[entityType] is None:
                return cls.metadataEntities[entityType](params)
            # otherwise check current count against maximum count
            elif cls.currentCount[entityType] < cls.maxCounts[entityType] -1:
                cls.currentCount[entityType] += 1
                return cls.metadataEntities[entityType](params)
            else:
                raise MetadataSchemeException("Too many instances of '{}' element (max multiplicity = {})".format(cls.metadataEntities[entityType].name, cls.maxCounts[entityType]))

    @classmethod
    def checkMinCounts(cls):
        missingElementTypes = []
        for entityType, entityClass in cls.metadataEntities.items():
            if cls.currentCount[entityType] < entityClass.minMultiplicity:
                missingElementTypes.append(entityClass.name)

        return missingElementTypes

class MetadataEntity:
    """
    Top level abstract class of the metadata entity. Defines metadata elements interface
    """

    # entity ID in metadata scheme
    ID = None
    # entity name
    name = None
    # description of the entity (= definition in BonaRes scheme)
    description = None
    # lowest number of appearances in resource, also works as optional/mandatory indicator
    minMultiplicity = 0
    # highest number of appearances in resource (None meaning infinity)
    maxMultiplicity = None
    # class of the super-element
    subtypeOf = None
    # data type that the element can be
    dataType = None
    # value domain the element can have
    domain = None
    # list of keywords used for identification of the element in the data resource
    keywords = None

    def __init__(self, value):
        # the actual value of the metadata element
        self.value = value
        # list of child metadata elements
        self.childElements = []
        # the parent element of self
        self.parentElement = None

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

class GeographicalMetadataEntity(MetadataEntity):
    """
    Abstract interface of metadata element with geographical value
    """
    def __init__(self, coordinateSystem, epsg = None):
        # the coordinate system of the element
        self.coordinateReferenceSystem = coordinateSystem
        # the EPSG code of the coordinate system of the element
        self.EPSGcode = epsg

class Title(TextMetadataEntity):
    ID = "1"
    name = "Title"
    description = "A characteristic, unique name by which the dataset is known."
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["title", "<h1>"]

    def __str__(self):
        return "metadata entity 'Title'"

EntityManager.registerMetadataEntityType(Title.name, Title.minMultiplicity, Title.maxMultiplicity)

class AlternateTitle(TextMetadataEntity):
    ID = "2"
    name = "Alternate title"
    description = "A short name by which the dataset is also known."
    minMultiplicity = 0
    maxMultiplicity = None
    keywords = ["<h2>"]
EntityManager.registerMetadataEntityType(AlternateTitle.name, AlternateTitle.minMultiplicity, AlternateTitle.maxMultiplicity)

class Summary(TextMetadataEntity):
    ID = "3"
    name = "Summary"
    description = "Brief narrative summary of the content of the dataset."
    minMultiplicity = 1
    maxMultiplicity = None
    keywords = ["<h2>"]
EntityManager.registerMetadataEntityType(Summary.name, Summary.minMultiplicity, Summary.maxMultiplicity)

class GraphicOverview(MetadataEntity):
    ID = "4"
    name = "Graphic overview"
    description = "Graphic that provides an illustration of the dataset."
    minMultiplicity = 0
    maxMultiplicity = None
    keywords = ["scheme"]
EntityManager.registerMetadataEntityType(GraphicOverview.name, GraphicOverview.minMultiplicity, GraphicOverview.maxMultiplicity)

class Date(MetadataEntity):
    ID = "5"
    name = "Date"
    description = "The date when the dataset was or will be made ..."
    minMultiplicity = 4
    maxMultiplicity = None
    keywords = ["date"]
EntityManager.registerMetadataEntityType(Date.name, Date.minMultiplicity, Date.maxMultiplicity)

class DateAccapted(MetadataEntity):
    ID = "5.1"
    name = "Date accepted"
    description = "The date that the publisher accepted the resource into their system."
    subtypeOf = Date
    minMultiplicity = 0
    maxMultiplicity = 1
    keywords = ["accapted"]
EntityManager.registerMetadataEntityType(DateAccapted.name, DateAccapted.minMultiplicity, DateAccapted.maxMultiplicity)

class DateAvailable(MetadataEntity):
    ID = "5.2"
    name = "Date available"
    description = "The date the resource was or will be made publicly available."
    subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["available"]
EntityManager.registerMetadataEntityType(DateAvailable.name, DateAvailable.minMultiplicity, DateAvailable.maxMultiplicity)

class DateCollected(MetadataEntity):
    ID = "5.3"
    name = "Date collected"
    description = "The date or date range in which the dataset content was collected."
    subtypeOf = Date
    minMultiplicity = 0
    maxMultiplicity = 2
    keywords = ["collected"]
EntityManager.registerMetadataEntityType(DateCollected.name, DateCollected.minMultiplicity, DateCollected.maxMultiplicity)

class DateCopyrighted(MetadataEntity):
    ID = "5.4"
    name = ""
    description = "The specific, documented date at which the dataset receives a copyrighted status, if applicable."
    subtypeOf = Date
    minMultiplicity = 0
    maxMultiplicity = 1
    keywords = ["copyrighted", "copyright"]
EntityManager.registerMetadataEntityType(DateCopyrighted.name, DateCopyrighted.minMultiplicity, DateCopyrighted.maxMultiplicity)

class DateCreated(MetadataEntity):
    ID = "5.5"
    name = ""
    description = "The date the dataset itself was put together; a single date for a final component (e.g. the finalised file with all of the data)."
    subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["created"]
EntityManager.registerMetadataEntityType(DateCreated.name, DateCreated.minMultiplicity, DateCreated.maxMultiplicity)

class DateIssued(MetadataEntity):
    ID = "5.6"
    name = ""
    description = "The date that the dataset is published or distributed to the data centre."
    subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["issued"]
EntityManager.registerMetadataEntityType(DateIssued.name, DateIssued.minMultiplicity, DateIssued.maxMultiplicity)

class DateSubmitted(MetadataEntity):
    ID = "5.7"
    name = ""
    description = "The date the author submits the resource to the publisher. This could be different from “Accepted” if the publisher then applies a selection process."
    subtypeOf = Date
    minMultiplicity = 0
    maxMultiplicity = 1
    keywords = ["submitted"]
EntityManager.registerMetadataEntityType(DateSubmitted.name, DateSubmitted.minMultiplicity, DateSubmitted.maxMultiplicity)

class DateUpdated(MetadataEntity):
    ID = "5.7"
    name = ""
    description = "The date of the last update (last revision) to the dataset, when the dataset is being added to."
    subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["updated", "update", "revised", "revision"]
EntityManager.registerMetadataEntityType(DateUpdated.name, DateUpdated.minMultiplicity, DateUpdated.maxMultiplicity)

class DateValid(MetadataEntity):
    ID = "5.8"
    name = ""
    description = "The date or date range during which the dataset or resource is accurate."
    subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["valid", "valid until"]
EntityManager.registerMetadataEntityType(DateValid.name, DateValid.minMultiplicity, DateValid.maxMultiplicity)

class GeographicalBoundingBox(GeographicalMetadataEntity):
    ID = "9"
    name = ""
    description = "The spatial limits of a box. A box is defined by two geographic points.\
    Lower left corner and upper right corner. Each point is defined by its longitude and latitude value."
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["bounding box", "extent", "geographical"]

    def __init__(self, northLat, southLat, westLong, eastLong, coordinateSystem, epsg = None):
        super(GeographicalBoundingBox, self).__init__(coordinateSystem, epsg)
        self.nortLatitude = northLat
        self.southLatitude = southLat
        self.westLongitude = westLong
        self.eastLongitude = eastLong
        return
EntityManager.registerMetadataEntityType(GeographicalBoundingBox.name, GeographicalBoundingBox.minMultiplicity, GeographicalBoundingBox.maxMultiplicity)

class TemporalExtent(MetadataEntity):
    ID = "11"
    name = ""
    description = "The time period in which the resource content was collected (e.g. From 2008-01-01 to 2008-12-31)"
    minMultiplicity = 0
    maxMultiplicity = 1
    keywords = ["temporal extent"]

EntityManager.registerMetadataEntityType(TemporalExtent.name, TemporalExtent.minMultiplicity, TemporalExtent.maxMultiplicity)
