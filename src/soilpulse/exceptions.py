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