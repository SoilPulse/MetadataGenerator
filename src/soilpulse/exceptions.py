# -*- coding: utf-8 -*-
"""
@author: Jan Devátý
"""

class MetadataSchemeException(Exception):
    """
    This exception is raised when there's some inconsistency in the resource's metadata structure
    """
    def __init__(self, message):
        self.message = "Metadata structure error:\n" + message

class ValueNotInDomainError(Exception):
    """
    This exception is raised when instance is initialized with value not present in class' allowed values list
    """
    def __init__(self, message):
        self.message = "Value not in domain:\n" + message

class DOIdataRetrievalException(Exception):
    """
    This exception is raised whenever there's something wrong about DOI data retrieval and manipulation
    """
    def __init__(self, message):
        self.message = "DOI processing error:\n" + message

class LocalFileManipulationError(Exception):
    """
    This exception is raised when there's something wrong with local files manipulation
    """

    def __init__(self, message):
        self.message = "Problem occured while manipulating files on SoilPulse server:\n" + message

class ContainerStructureError(Exception):

    def __init__(self, message):
        self.message = "Container with provided ID couldn't be found/created:\n" + message

class DatabaseFetchError(Exception):
    """
    This exception is raised when there's something wrong with data retrieval from SoilPulse database
    """
    def __init__(self, message):
        self.message = "SoilPulse couldn't fetch requested entry:\n" + message

class DatabaseEntryError(Exception):

    def __init__(self, message):
        self.message = "SoilPulse database consistency error:\n" + message

class NameNotUniqueError(Exception):
    def __init__(self, message):
        self.message = "Provided name is not unique:\n" + message

class DeserializationError(Exception):
    """
    This exception is raised when there's something wrong with data being read from a serialization
    """
    def __init__(self, message):
        self.message = "Error appeared while trying to deserialize JSON-saved data:\n" + message
