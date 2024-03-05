# coding = utf-8
# -*- coding: utf-8 -*-

import os
import re
import csv
import io
from collections import Counter

from src.soilpulse.resource_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler
from src.soilpulse.db_access import EntityKeywordsDB
# just for the standalone functions - will be changed
from src.soilpulse.resource_management import *

type = 'filesystem'
format = "File system"
keywordsDBfilename = "keywords_filesystem"

class FileSystemContainer(ContainerHandler):
    containerType = type
    containerFormat = format
    keywordsDBname = keywordsDBfilename
    def __init__(self, name, downloadDir, doi=None):
        super(FileSystemContainer, self).__init__(name, doi)
        # list of all the directories that belong to the repository
        self.directories = []
        # list of all the files that belong to the repository
        self.sourceURLs = []
        # directory where the script will have access to write
        self.downloadDir = downloadDir

        if doi:
            response = getFileListOfDOI(doi)
            print("dict of info from Zenodo:")
            for item in response:
                for key, value in item.items():
                    print("{}: {}".format(key, value))
                print("\n")
            # self.sourceURLs.extend(URLlist)
            # self.downloadFiles(URLlist, self.downloadDir, True)

ContainerHandlerFactory.registerContainerType(FileSystemContainer, FileSystemContainer.containerType)
EntityKeywordsDB.registerKeywordsDB(FileSystemContainer.containerType, FileSystemContainer.keywordsDBname)

class FileSystemPointer(Pointer):

    pointerType = type

    def __init__(self, filename, startChar, numChars):
        # full path to the file of appearance
        self.filename = filename
        # index of place where the value starts
        self.startChar = startChar
        # length of the value in characters
        self.numChars = numChars
        pass

    pass


class FilesystemCrawler(Crawler):
    """
    Crawler for file system repositories
    """

    def __init__(self, filepath):
        self.file = filepath

    def crawl(self):
        """
        Do the crawl - go through the file and detect defined elements
        """

        tables = self.findCSVtables(2)
        print(tables)

    def findCSVtables(self, min_lines=3):
        # Pattern to match CSV-like tables without knowing delimiters
        pattern = r'\b[\w\s]+(?:[^\w\s]+[\w\s]+)*\b'

        # read the file into a text
        with open(self.file, 'r') as file:
            text = file.read()

        # Find all matches
        matches = re.findall(pattern, text)

        # Filter matches based on structure (e.g., number of lines)
        table_like_matches = [match for match in matches if match.count('\n') >= min_lines]

        return table_like_matches


def detect_delimiters(text):
    """
    Detect line, cell and decimal delimiters used in input file based on first table found in file
    """

    # Use Sniffer to infer the dialect
    csv_file = io.StringIO(text)
    dialect = csv.Sniffer().sniff(csv_file.read(1024))  # Read a portion of the text for analysis

    # Analyze numeric values to detect the decimal separator
    decimal_separator = detect_decimal_separator(text, dialect.delimiter)

    return dialect.delimiter, dialect.lineterminator, decimal_separator


def detect_decimal_separator(text, delimiter):
    # Split the text into rows and columns
    rows = [line.split(delimiter) for line in text.splitlines() if line.strip()]

    # Flatten the list of values
    values = [value for row in rows for value in row]

    # Extract numeric values
    numeric_values = [value for value in values if is_numeric(value)]

    # Count occurrences of decimal separators
    decimal_separator_counts = Counter(
        value.replace(',', '') for value in numeric_values if ',' in value or '.' in value)

    # Determine the most common decimal separator
    most_common_decimal_separator = decimal_separator_counts.most_common(1)

    if most_common_decimal_separator:
        return most_common_decimal_separator[0][0]
    else:
        return None


def is_numeric(value):
    try:
        float(value.replace(',', ''))
        return True
    except ValueError:
        return False