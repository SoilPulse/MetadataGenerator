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
    This exception is raised when instance is initialized with value not present in class' allowe values list
    """
    def __init__(self, message):
        self.message = "Value not in domain:\n" + message

class DOIdataRetrievalException(Exception):
    """
    This exception is raised whenever there's something wrong about DOI data retrieval and manipulation
    """
    def __init__(self, message):
        self.message = "DOI processing error:\n" + message

class DatabaseFetchError(Exception):
    """
    This exception is raised when there's something wrong with data retrieval from SoilPulse database
    """
    def __init__(self, message):
        self.message = "Values requested from SoilPulse were not found:\n" + message

class LocalFileManipulationError(Exception):
    """
    This exception is raised when there's something wrong with local files manipulation
    """

    def __init__(self, message):
        self.message = "Problem occured while manipulating files on SoilPulse server:\n" + message