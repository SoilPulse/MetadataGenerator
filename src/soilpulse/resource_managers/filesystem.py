# coding = utf-8
# -*- coding: utf-8 -*-

import os
import re
import csv
import io
import datetime
from collections import Counter
# import magic

from src.soilpulse.resource_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler
from src.soilpulse.db_access import EntityKeywordsDB
# just for the standalone functions - will be changed
from src.soilpulse.resource_management import *

class FileSystemContainer(ContainerHandler):
    containerType = 'filesystem'
    containerFormat = "File system"
    keywordsDBname = "keywords_filesystem"

    def __init__(self, name, path):
        super(FileSystemContainer, self).__init__(name)
        # the file type
        self.path = path
        # get mime type of the file
        self.mimeType = self.getMimeType()
        # get other useful of the file (size, date of creation ...)
        self.size = None
        self.dateCreated = datetime.datetime.fromtimestamp(os.path.getctime(path))
        self.dateLastModified = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        # extension
        self.fileExtension = path.split(".")[-1]
        # if the file is zip - unpack and create the containers from content
        if self.fileExtension == "zip":
            self.containers = self.extractZipFile(self.path)

        elif os.path.isfile(self.path):
            self.crawler = FilesystemCrawler(self.path)

    def showContents(self, depth = 0, ind = ". "):
        """
        Print basic info about the container and invokes showContents on all of its containers

        :param depth: current depth of showKeyValueStructure recursion
        :param ind: string of a single level indentation
        """
        t = ind * depth
        dateFormat = "%d.%m.%Y"
        print("{}{} - {} ({}, {}, {}/{}) [{}]".format(t, self.id, self.name, self.containerType, self.getFileSizeFormated(), self.dateCreated.strftime(dateFormat), self.dateLastModified.strftime(dateFormat), len(self.containers)))

        if self.containers:
            depth += 1
            for cont in self.containers:
                cont.showContents(depth)

    def getMimeType(self):
        # self.mimeType = magic.from_file(self.path)
        return

    def getFileSize(self):
        return os.stat(self.path).st_size if os.path.isfile(self.path) else None

    def getFileSizeFormated(self):
        suffix = "B"
        size = self.getFileSize()
        if size:
            for unit in ("", "k", "M", "G", "T", "P", "E", "Z"):
                if abs(size) < 1024.0:
                    return f"{size:3.1f} {unit}{suffix}"
                size /= 1024.0
            return f"{size:.1f}Yi{suffix}"
        else:
            return None

    def extractZipFile(self, theZip, targetDir = None, removeZip = True):
        from zipfile import ZipFile, BadZipfile

        extractDirName = ".".join(os.path.basename(theZip).split(".")[:-1])+"_zip"
        outDir = targetDir if targetDir else os.path.join(os.path.dirname(theZip), extractDirName)
        try:
            print("\t\textracting to '{}'".format(outDir))
            with ZipFile(theZip) as my_zip_file:
                my_zip_file.extractall(outDir)
        except BadZipfile:
            print("File '{}' is not a valid ZIP archive and couldn't be extracted".format(theZip))
        else:
            if removeZip:
                try:
                    os.remove(theZip)
                except OSError:
                    print("\nFile '{}' couldn't be deleted. It may be locked by another application.".format(theZip))

            self.path = extractDirName
            return self.createTree(outDir, "")

    def createTree(self, folder, t = ""):
        tree = []
        for f in os.listdir(folder):
            fullpath = os.path.join(folder, f)
            if os.path.isfile(fullpath):
                tree.append(ContainerHandlerFactory.createHandler('filesystem', f, fullpath))
            elif os.path.isdir(os.path.join(folder, f)):
                t += "\t"
                dirCont = ContainerHandlerFactory.createHandler('filesystem', f, fullpath)
                dirCont.containers = self.createTree(fullpath, t)
                tree.append(dirCont)

            else:
                print("{} /// weird {}".format(t, os.path.join(folder, f)))

        return tree



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