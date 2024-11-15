# -*- coding: utf-8 -*-
"""
@author: Jan Devátý
"""


from .exceptions import DatabaseFetchError, ValueNotInDomainError
from .db_access import EntitySearchPatternsDB
from .db_access import EntityKeywordsDB

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
    # collection of all search patterns from all MetadataEntity subclasses
    searchPatterns = {}
    keywordPatterns = {}
    # kyewords database to load keywords from
    keywordDatabases = {}

    # _instance = None
    def __init__(self):

        return

    @classmethod
    def registerMetadataEntityType(cls, entityClass):
        cls.metadataEntities[entityClass.key] = entityClass
        cls.minCounts[entityClass.key] = entityClass.minMultiplicity
        cls.maxCounts[entityClass.key] = entityClass.maxMultiplicity
        cls.currentCount[entityClass.key] = 0

        # connect to local database and load search patterns and keywords for the entity type being registered
        try:
            # get the search expressions from the DB for the entity type
            search_patterns = EntitySearchPatternsDB.loadSearchPatterns(entityClass)
            # if something found put it in class' search_patterns dict
            if search_patterns:
                entityClass.searchPatterns = search_patterns

            # get the search keywords from the DB for the entity type
            keywords = EntityKeywordsDB.loadKeywords(entityClass)
            if keywords:
                entityClass.keywords = keywords

            # entityClass.showSearchPhrases()

        except DatabaseFetchError as e:
            print(e)
        else:
            # and if successful put them into the entity managers mapping
            cls.searchPatterns.update({entityClass.key: entityClass.searchPatterns})
            cls.keywordPatterns.update({entityClass.key: entityClass.keywords})

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
    def showSearchExpressions(cls):
        print("\nEntityManager search patterns:")
        for k,v in cls.searchPatterns.items():
            if len(v) > 0:
                print("\t{}".format(k))
                for l, w in v.items():
                    print("\t\t{}: {}".format(l, w))
            else:
                print("\t{}: None".format(k))

        print("\nEntityManager keywords search patterns:")
        for k,v in cls.keywordPatterns.items():
            if len(v) > 0:
                print("\t{}".format(k))
                for l, w in v.items():
                    print("\t\t{}: {}".format(l, w))
            else:
                print("\t{}: None".format(k))

        return

    @classmethod
    def showEntityCount(cls):
        print("\ncurrent entity count:")
        for k,v in cls.currentCount.items():
            print("{}: {}".format(k,v))
        return


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
    # lowest number of appearances in dataset, also works as optional/mandatory indicator
    minMultiplicity = 0
    # highest number of appearances in dataset (None meaning infinity)
    maxMultiplicity = None
    # ? class of the super-element
    subtypeOf = None
    # ? data type that the element can be
    dataType = None
    # ? value domain the element can have
    domain = None
    # dictionary of regular expressions used for identification of the element in the data resource { local group name: search pattern, ...}
    searchPatterns = {}
    # dictionary of keywords used for identification of the element in the data resource { local group name: keyword, ...}
    # this waythe keywords are translatable but need to be converted to search patterns before use
    keywords = {}

    def __init__(self, sourceString, value = None):
        # the piece of text from which the value was derived
        self.sourceString = sourceString
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

    @classmethod
    def showSearchPhrases(cls):
        print("search patterns of '{}':".format(cls.name))
        print(cls.searchPatterns)
        print("keywords of '{}':".format(cls.name))
        print(cls.keywords)
        return

class TextMetadataEntity(MetadataEntity):
    """
    Abstract interface class of metadata element with textual value
    """

    def __init__(self, value, language, encoding):
        # the actual value of the metadata element
        super().__init__(value)
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
        super().__init__(value)
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


class SubjectMetadataEntity(MetadataEntity):
    """
    Abstract interface class of metadata element that represents a person or an institution that is responsible
    for producing (collecting, managing, distributing, or otherwise contributing to the development of the
    dataset) the data, or has relation to authors of the publication
    """

    roleTypes = {}
    def __init__(self, value):
        # the actual value of the metadata element
        super().__init__(value)

        return


class Title(TextMetadataEntity):
    ID = "1"
    key = "title"
    name = "Title"
    description = "A characteristic, unique name by which the dataset is known."
    minMultiplicity = 1
    maxMultiplicity = 1

    def __str__(self):
        return "metadata entity 'Title'"

EntityManager.registerMetadataEntityType(Title)

class AlternateTitle(TextMetadataEntity):
    ID = "2.1"
    key = "alternate_title"
    name = "Alternate title"
    description = "A short name by which the dataset is also known."
    minMultiplicity = 0
    maxMultiplicity = 1

EntityManager.registerMetadataEntityType(AlternateTitle)

class Subtitle(TextMetadataEntity):
    ID = "2.2"
    key = "subtitle"
    name = "Subtitle"
    description = ""
    minMultiplicity = 0
    maxMultiplicity = 1

EntityManager.registerMetadataEntityType(Subtitle)

class TranslatedTitle(TextMetadataEntity):
    ID = "2.3"
    key = "translated_title"
    name = "Subtitle"
    description = ""
    minMultiplicity = 0
    maxMultiplicity = 1

EntityManager.registerMetadataEntityType(TranslatedTitle)

class OtherAlternateTitle(TextMetadataEntity):
    ID = "2.4"
    key = "other_alternate_title"
    name = "Other alternate title"
    description = ""
    minMultiplicity = 0
    maxMultiplicity = 1

EntityManager.registerMetadataEntityType(OtherAlternateTitle)

class Summary(TextMetadataEntity):
    ID = "3"
    key = "summary"
    name = "Summary"
    description = "Brief narrative summary of the content of the dataset."
    minMultiplicity = 1
    maxMultiplicity = None

EntityManager.registerMetadataEntityType(Summary)

class GraphicOverview(MetadataEntity):
    ID = "4"
    key = "graphic_overview"
    name = "Graphic overview"
    description = "Graphic that provides an illustration of the dataset."
    minMultiplicity = 0
    maxMultiplicity = None

EntityManager.registerMetadataEntityType(GraphicOverview)

class DateAccapted(DateMetadataEntity):
    ID = "5.1"
    key = "date_accepted"
    name = "Date accepted"
    description = "The date that the publisher accepted the resource into their system."
    minMultiplicity = 0
    maxMultiplicity = 1

EntityManager.registerMetadataEntityType(DateAccapted)

class DateAvailable(DateMetadataEntity):
    ID = "5.2"
    key = "date_available"
    name = "Date available"
    description = "The date the resource was or will be made publicly available."
    minMultiplicity = 1
    maxMultiplicity = 1

EntityManager.registerMetadataEntityType(DateAvailable)

class DateCollected(DateMetadataEntity):
    ID = "5.3"
    key = "date_collected"
    name = "Date collected"
    description = "The date or date range in which the dataset content was collected."
    minMultiplicity = 0
    maxMultiplicity = 2

EntityManager.registerMetadataEntityType(DateCollected)

class DateCopyrighted(DateMetadataEntity):
    ID = "5.4"
    key = "date_copyrighted"
    name = "Date copyrighted"
    description = "The specific, documented date at which the dataset receives a copyrighted status, if applicable."
    minMultiplicity = 0
    maxMultiplicity = 1

EntityManager.registerMetadataEntityType(DateCopyrighted)

class DateCreated(DateMetadataEntity):
    ID = "5.5"
    key = "date_created"
    name = "Date created"
    description = "The date the dataset itself was put together; a single date for a final component (e.g. the finalised file with all of the data)."
    minMultiplicity = 1
    maxMultiplicity = 1

EntityManager.registerMetadataEntityType(DateCreated)

class DateIssued(DateMetadataEntity):
    ID = "5.6"
    key = "date_issued"
    name = "Date issued"
    minMultiplicity = 1
    maxMultiplicity = 1

EntityManager.registerMetadataEntityType(DateIssued)

class DateSubmitted(DateMetadataEntity):
    ID = "5.7"
    key = "date_submitted"
    name = "Date submitted"
    description = "The date the author submits the resource to the publisher. This could be different from “Accepted” if the publisher then applies a selection process."
    minMultiplicity = 0
    maxMultiplicity = 1

EntityManager.registerMetadataEntityType(DateSubmitted)

class DateUpdated(DateMetadataEntity):
    ID = "5.8"
    key = "date_updated"
    name = "Date updated"
    description = "The date of the last update (last revision) to the dataset, when the dataset is being added to."
    minMultiplicity = 1
    maxMultiplicity = 1

EntityManager.registerMetadataEntityType(DateUpdated)

class DateValid(DateMetadataEntity):
    ID = "5.9"
    key = "date_valid"
    name = "Date valid"
    description = "The date or date range during which the dataset or resource is accurate."
    minMultiplicity = 0
    maxMultiplicity = 1

EntityManager.registerMetadataEntityType(DateValid)

class ResponsiblePerson(SubjectMetadataEntity):
    ID = "6.1"
    key = "responsible_person"
    name = "Responsible person"
    description = "Person involved in producing (collecting, managing, distributing, or otherwise\
            contributing to the development of the dataset) the data, or the authors of the publication, \
            in priority order. Will be cited if Author is used as contact type."
    minMultiplicity = 2
    maxMultiplicity = None

    # supported roleType values list
    roleTypes = {"Data Collector": 0,
                 "Data Curator": 0,
                 "Editor": 0,
                 "Producer": 0,
                 "Project leader": 1,
                 "Project manager": 0,
                 "Project member": 0,
                 "Related person": 0,
                 "Researcher": 0,
                 "Rights Holder": 0,
                 "Sponsor": 0,
                 "Supervisor": 0,
                 "Work package leader": 0,
                 "Author": 1,
                 "Custodian": 0,
                 "Originator": 0,
                 "Owner": 0,
                 "Point of contact": 0,
                 "Principal investigator": 0,
                 "Processor": 0,
                 "User": 0
                 }

    def __init__(self, roleType):
        # the roleType needs to be checked against ResponsiblePerson allowed roleTypes list
        self.__roleType = self.setRoleType(roleType)

        self.familyName = None
        self.givenName = None
        self.organization = None
        self.position = None
        # list of Identifier MetadataEntity instances
        self.identifiers = []
        self.phone =  None
        self.fascimile = None
        # an Address MetadataEntity instance
        self.address = None
        self.email = None



    def setRoleType(self, roleType):
        """
        Setter for private __roleType attribute
        """
        if roleType not in ResponsiblePerson.roleTypes.keys():
            raise ValueNotInDomainError("'{}' role is not supported for {}\nSupported role types are: {}".format(roleType, type(ResponsiblePerson), ", ".join(["'"+r+"'" for r in ResponsiblePerson.roleTypes.keys()])))
        else:
            self.__roleType = roleType

EntityManager.registerMetadataEntityType(ResponsiblePerson)

class ResponsibleOrganization(SubjectMetadataEntity):
    ID = "6.2"
    key = "responsible_organization"
    name = "Responsible organization"
    description = "Institution involved in producing (collecting, managing, distributing, or otherwise\
            contributing to the development of the dataset) the data, or having a relation to the authors of the publication, \
            in priority order."
    minMultiplicity = None
    maxMultiplicity = None
    # supported roleType values list
    roleTypes = {"Hosting institution": 0,
                 "Registration agency": 0,
                 "Registration authority": 0,
                 "Research group": 0,
                 "Rights Holder": 0,
                 "Sponsor": 0,
                 "Distributor": 0,
                 "Owner": 0,
                 "Point of contact": 0,
                 "Processor": 0,
                 "Publisher": 0,
                 "Resource provider": 0
                 }

    def __init__(self, roleType):
        # the roleType needs to be checked against allowed roleTypes list
        self.__roleType = self.setRoleType(roleType)

    def setRoleType(self, roleType):
        """
        Setter for private __roleType attribute
        """
        if roleType not in ResponsibleOrganization.roleTypes.keys():
            raise ValueNotInDomainError("'{}' role is not supported for {}\nSupported role types are: {}".format(roleType, type(ResponsibleOrganization), ", ".join(["'"+r+"'" for r in ResponsibleOrganization.roleTypes.keys()])))
        else:
            self.__roleType = roleType

EntityManager.registerMetadataEntityType(ResponsibleOrganization)

class FundingReference(MetadataEntity):
    ID = "7"
    key = "funding_reference"
    name = "Funding reference"
    description = "Information about financial support (funding) for the dataset being registered."
    minMultiplicity = 1
    maxMultiplicity = None

EntityManager.registerMetadataEntityType(FundingReference)
#
#
# class Dummy(MetadataEntity):
#     ID = ""
#     key = ""
#     name = ""
#     description = ""
#     minMultiplicity = None
#     maxMultiplicity = None
#
# EntityManager.registerMetadataEntityType()

class GeographicalBoundingBox(GeographicalMetadataEntity):
    ID = "9"
    key = "bounding_box"
    name = "Geographical bounding box"
    description = "The spatial limits of a box. A box is defined by two geographic points.\
    Lower left corner and upper right corner. Each point is defined by its longitude and latitude value."
    minMultiplicity = 1
    maxMultiplicity = 1

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

    def __init__(self):
        self.start = None
        self.end = None

EntityManager.registerMetadataEntityType(TemporalExtent)
