# -*- coding: utf-8 -*-
"""
@author: Jan Devátý
"""

class MetadataEntity:
    """
    Top level abstract class of the metadata entity
    """

    # entity ID in metadata scheme
    ID = None
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
    description = "A characteristic, unique name by which the dataset is known."
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["title", "<h1>"]

class AlternateTitle(TextMetadataEntity):
    ID = "2"
    description = "A short name by which the dataset is also known."
    minMultiplicity = 0
    maxMultiplicity = None
    keywords = ["<h2>"]

class Summary(TextMetadataEntity):
    ID = "3"
    description = "Brief narrative summary of the content of the dataset."
    minMultiplicity = 1
    maxMultiplicity = None
    keywords = ["<h2>"]

class GraphicOverview(MetadataEntity):
    ID = "4"
    description = "Graphic that provides an illustration of the dataset."
    minMultiplicity = 0
    maxMultiplicity = None
    keywords = ["scheme"]

class Date(MetadataEntity):
    ID = "5"
    description = "The date when the dataset was or will be made ..."
    minMultiplicity = 4
    maxMultiplicity = None
    keywords = ["date"]

class DateAccapted(MetadataEntity):
    ID = "5.1"
    description = "The date that the publisher accepted the resource into their system."
    subtypeOf = Date
    minMultiplicity = 0
    maxMultiplicity = 1
    keywords = ["accapted"]

class DateAvailable(MetadataEntity):
    ID = "5.2"
    description = "The date the resource was or will be made publicly available."
    subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["available"]

class DateCollected(MetadataEntity):
    ID = "5.3"
    description = "The date or date range in which the dataset content was collected."
    subtypeOf = Date
    minMultiplicity = 0
    maxMultiplicity = 2
    keywords = ["collected"]

class DateCopyrighted(MetadataEntity):
    ID = "5.4"
    description = "The specific, documented date at which the dataset receives a copyrighted status, if applicable."
    subtypeOf = Date
    minMultiplicity = 0
    maxMultiplicity = 1
    keywords = ["copyrighted", "copyright"]

class DateCreated(MetadataEntity):
    ID = "5.5"
    description = "The date the dataset itself was put together; a single date for a final component (e.g. the finalised file with all of the data)."
    subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["created"]

class DateIssued(MetadataEntity):
    ID = "5.6"
    description = "The date that the dataset is published or distributed to the data centre."
    subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["issued"]

class DateSubmitted(MetadataEntity):
    ID = "5.7"
    description = "The date the author submits the resource to the publisher. This could be different from “Accepted” if the publisher then applies a selection process."
    subtypeOf = Date
    minMultiplicity = 0
    maxMultiplicity = 1
    keywords = ["submitted"]

class DateUpdated(MetadataEntity):
    ID = "5.7"
    description = "The date of the last update (last revision) to the dataset, when the dataset is being added to."
    subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["updated", "update", "revised", "revision"]

class DateValid(MetadataEntity):
    ID = "5.8"
    description = "The date or date range during which the dataset or resource is accurate."
    subtypeOf = Date
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["valid", "valid until"]

class GeographicalBoundingBox(GeographicalMetadataEntity):
    ID = "9"
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

class TemporalExtent(MetadataEntity):
    ID = "11"
    description = "The time period in which the resource content was collected (e.g. From 2008-01-01 to 2008-12-31)"
    minMultiplicity = 0
    maxMultiplicity = 1
    keywords = ["temporal extent"]