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

    subtypeOf = None

    dataType = None

    domain = None
    # list of keywords used for identification of the element in the data resource
    keywords = None

    def __init__(self, value):
        self.value = value

class TextualEnity(MetadataEntity):
    """
    Abstract interface class of textual value metadata entity
    """
    translations = []
    def __init__(self, value, language):
        self.value = value
        self.language = language

class Title(MetadataEntity, TextualEnity):
    ID = "1"
    description = "A characteristic, unique name by which the dataset is known."
    minMultiplicity = 1
    maxMultiplicity = 1
    keywords = ["title", "<h1>"]

class AlternateTitle(MetadataEntity, TextualEnity):
    ID = "2"
    description = "A short name by which the dataset is also known."
    minMultiplicity = 0
    maxMultiplicity = None
    keywords = ["<h2>"]

class Summary(MetadataEntity, TextualEnity):
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

