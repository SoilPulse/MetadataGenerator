# coding = utf-8
# -*- coding: utf-8 -*-

import os
import re
import csv
import io
import datetime
from collections import Counter
import chardet
import pandas as pd
# import magic

from src.soilpulse.resource_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler
from src.soilpulse.db_access import EntityKeywordsDB
# just for the standalone functions - will be changed
from src.soilpulse.resource_management import *


def detect_encoding(input_file):
    # If it's not a string, assume it's a file path and read the contents
    with open(input_file, 'rb') as file:
        rawdata = file.read()

    result = chardet.detect(rawdata)
    encoding = result['encoding']
    confidence = result['confidence']
    return encoding, confidence

def convert_tables_to_dataframes(text, table_structures):
    dfs = []
    for start, length in table_structures:
        table_text = text[start:start+length]
        lines = table_text.split('\n')
        rows = [line.split(',') for line in lines]
        df = pd.DataFrame(rows[1:], columns=rows[0])
        dfs.append(df)
    return dfs

def detect_delimiters(text):
    """
    Detect line, cell and decimal delimiters used in input file based on first table found in file
    """

    # Use Sniffer to infer the dialect
    csv_file = io.StringIO(text)
    dialect = csv.Sniffer().sniff(csv_file.read(2048))  # Read a portion of the text for analysis

    return dialect.delimiter, dialect.lineterminator


class FileSystemContainer(ContainerHandler):
    containerType = 'filesystem'
    containerFormat = "File system"
    keywordsDBname = "keywords_filesystem"


    def __init__(self, id, name, path):
        super(FileSystemContainer, self).__init__(id, name)
        # the file path
        self.path = path
        # get mime type of the file
        self.mimeType = self.getMimeType()
        # get other useful of the file (size, date of creation ...)
        self.size = None
        self.dateCreated = datetime.datetime.fromtimestamp(os.path.getctime(path))
        self.dateLastModified = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        self.encoding = None
        self.fileExtension = None
        self.crawler = None

        if os.path.isfile(path):
            # extension
            self.fileExtension = path.split(".")[-1]
            # if the file is zip - unpack and create the containers from content
            if self.fileExtension == "zip":
                self.containers = self.extractZipFile(self.path)
            else:
                self.encoding = detect_encoding(path)[0]

                try:
                    self.crawler = FileSystemCrawlerFactory.createCrawler(self.fileExtension, self)
                except ValueError as e:
                    print(e)

    def showContents(self, depth = 0, ind = ". "):
        """
        Print basic info about the container and invokes showContents on all of its containers

        :param depth: current depth of showKeyValueStructure recursion
        :param ind: string of a single level indentation
        """
        t = ind * depth
        dateFormat = "%d.%m.%Y"
        print(f"{t}{self.id} - {self.name} ({self.containerType}, {self.getFileSizeFormated()}, {self.dateCreated.strftime(dateFormat)}/{self.dateLastModified.strftime(dateFormat)}) [{len(self.containers)}]")

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
        """
        Returns a string of dynamically formatted file size
        """
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

    def getCrawled(self):
        if self.crawler:
            tables = self.crawler.crawl()
            if tables:
                print(f"tables:\n{tables}")
                print("\n\n")
        for container in self.containers:
            container.getCrawled()


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


# class FilesystemCrawler(Crawler):
#     """
#     Crawler for file system repositories
#     """
#
#     def __init__(self, filesystemContainer):
#         self.path = filesystemContainer.path
#         # print("new file system crawled created")
#         pass
#
#     def crawl(self):
#         """
#         Do the crawl - go through the file and detect defined elements
#         """
#         print(f"crawling {self.path}")
#         dataframes = self.get_tables_from_csv(2)
#         if len(dataframes) > 0:
#             print(f"\tfound {len(dataframes)} understandable table structures")
#             return dataframes
#         else:
#             print(f"\tfound no understandable tables")
#             return None
#
#     def get_tables_from_csv(self, cell_delimiter, min_lines=3):
#         # encoding = detect_encoding(self.file)
#         # read the file into a text
#         with open(self.file, 'r', encoding='ANSI') as file:
#             text = file.read()
#         file_length = len(text)
#         # try detecting delimiters from file content
#         cell_sep, line_sep = detect_delimiters(text)
#         print(f"\tcell delimiter: '{cell_sep}'")
#
#         # Pattern to match CSV-like tables without knowing delimiters
#         # pattern = r'\b[\w\s]+(?:[^\w\s]+[\w\s]+)*\b'
#         pattern = r'(?:(?<!\w)[^\w\s]*(?:\w+\W*(?:\w+\W*)+\w+|\w+(?:\W+\w+)+\w+)\b(?:\W|\Z))'
#
#         # Find all matches and their start character and length
#         matches = re.finditer(pattern, text)
#         # Filter matches based on structure (e.g., number of lines) and store start character and length
#         table_dataframes = []
#         m = 0
#         for match in matches:
#             start_char = match.start()
#             length = match.end() - match.start()
#
#             # print(f"\nmatch {m}")
#             # match_string = text[match.start():match.end()]
#             # print(f"match string:\n{match_string}\nlength {len(match_string)}")
#
#             num_lines = text[match.start():match.end()].count('\n')
#             # print(f"number of lines {num_lines}")
#             if num_lines >= min_lines:
#                 print(f"\ttable detected starting at {start_char} with length {length} (of total {file_length} characters), spanning over {num_lines} lines")
#
#                 table_text = text[start_char: start_char + length]
#                 lines = table_text.split('\n')
#                 rows = [line.split(cell_sep) for line in lines]
#                 # replace possible empty cells in header
#                 unknown_i = 1
#                 i = 0
#                 for cell in rows[0]:
#                     # print(f"'{cell}'")
#                     if len(cell) == 0:
#                         print(f"\tempty value in header ('{cell}') replaced with generated name 'column_{unknown_i}")
#                         rows[0][i] = f"column_{unknown_i}"
#                         unknown_i += 1
#                     i += 1
#
#                 # check if the last row is all Nones
#                 num_nones = 0
#                 for cell in rows[-1]:
#                     if cell is None:
#                         num_nones += 1
#                 if num_nones == len(rows[-1]):
#                     rows.pop()
#                     print(f"\tlast row was all Nones and was removed")
#                 print(f"\tcolumn headers are: {rows[0]}")
#
#                 # try converting list of lists to pandas dataframe
#                 try:
#                     df = pd.DataFrame(rows[1:], columns=rows[0])
#                 except :
#                     print(f"File '{self.file}' has unknown structure.")
#
#                 else:
#                     table_dataframes.append(df)
#             m += 1
#
#         return table_dataframes

class FileSystemCrawlerFactory:
    """
    File system type crawler factory
    """

    # directory of registered publisher types classes
    filetypes = {}

    # the one and only instance
    _instance = None
    def __init__(self):

        def __new__(class_, *args, **kwargs):
            if not isinstance(class_._instance, class_):
                class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance

    @classmethod
    def registerFileType(cls, fileTypeCrawlerClass, key):
        cls.filetypes[key] = fileTypeCrawlerClass
        print(f"Crawler for file type '{key}' registered.")
        return

    @classmethod
    def createCrawler(cls, fileTypeKey, container, *args):
        """
        Creates and returns instance of Publisher of given key
        """

        if fileTypeKey:
            if fileTypeKey.lower() not in cls.filetypes.keys():
                filetypes = ",".join(["'"+k+"'" for k in cls.filetypes.keys()])
                print(f"\tUnsupported Crawler subclass type '{fileTypeKey.lower()}' (registered types are: {filetypes}) - plain text crawler will be used instead.")
                return cls.filetypes['txt'](container, *args)
            else:
                return cls.filetypes[fileTypeKey](container, *args)
        else:
            print(f"\tFile has no extension ... plain text crawler will be used instead.")
            return cls.filetypes['txt'](container, *args)

class CSVcrawler(Crawler):
    """
    Crawler for CSV tables
    """
    extension = "csv"
    def __init__(self, container):
        self.container = container

        # print(f"\tCSV crawler created for container #{self.container.id} '{self.container.name}' (file '{self.container.path}')")
        pass

    def crawl(self):
        """
        Do the crawl - go through the file and detect defined elements
        """
        print(f"crawling CSV '{self.container.path}' of container #{self.container.id}, encoding '{self.container.encoding}'")
        dataframes = self.get_tables_from_csv(2)
        if len(dataframes) > 0:
            print(f"\tfound {len(dataframes)} understandable table structures")
            return dataframes
        else:
            print(f"\tfound no understandable tables")
            return None

    def get_tables_from_csv(self, cell_delimiter, min_lines=3):
        # encoding = detect_encoding(self.file)
        # read the file into a text
        with open(self.container.path, 'r', encoding='ANSI') as file:
            text = file.read()
        file_length = len(text)
        # try detecting delimiters from file content
        cell_sep, line_sep = detect_delimiters(text)
        print(f"\tcell delimiter: '{cell_sep}'")

        # Pattern to match CSV-like tables without knowing delimiters
        pattern = r'(?:(?<!\w)[^\w\s]*(?:\w+\W*(?:\w+\W*)+\w+|\w+(?:\W+\w+)+\w+)\b(?:\W|\Z))'
        # pattern = r'(?:(?<!\w)[^\w\s]*(?:\w+\W*(?:\w+\W*)+\w+|\w+(?:\W+\w+)+\w+)\b(?:\W|$))(?!\n\s*$)'
        # pattern = r'(?:(?<!\w)[^\w\s]*(?:\w+\W*(?:\w+\W*)+\w+|\w+(?:\W+\w+)+\w+)\b(?:\W|$))(?=\n|\Z)'

        # Find all matches and their start character and length
        matches = re.finditer(pattern, text)
        # Filter matches based on structure (e.g., number of lines) and store start character and length
        table_dataframes = []
        m = 0
        for match in matches:
            start_char = match.start()
            length = match.end() - match.start()

            # print(f"\nmatch {m}")
            # match_string = text[match.start():match.end()]
            # print(f"match string:\n{match_string}\nlength {len(match_string)}")

            num_lines = text[match.start():match.end()].count('\n')
            # print(f"number of lines {num_lines}")
            if num_lines >= min_lines:
                print(f"\ttable detected starting at {start_char} with length {length} (of total {file_length} characters), spanning over {num_lines} lines")

                table_text = text[start_char: start_char + length]
                lines = table_text.split('\n')
                rows = [line.split(cell_sep) for line in lines]
                row_length = len(rows[0])
                # replace possible empty cells in header
                unknown_i = 1
                i = 0
                for cell in rows[0]:
                    # print(f"'{cell}'")
                    if len(cell) == 0:
                        print(f"\tempty value in header ('{cell}') replaced with generated name 'column_{unknown_i}")
                        rows[0][i] = f"column_{unknown_i}"
                        unknown_i += 1
                    else:
                        rows[0][i] = cell.strip('\"\'')
                    i += 1

                # check if the last row is empty
                if len(rows[-1]) < row_length:
                    print(f"\tthe last row was removed: {rows[-1]}")
                    rows.pop()
                # check if the last row is all Nones
                num_nones = 0
                for cell in rows[-1]:
                    if cell is None:
                        num_nones += 1
                if num_nones == len(rows[-1]):
                    rows.pop()
                    print(f"\tlast row was all Nones and was removed")

                print(f"\tcolumn headers are: {rows[0]}")

                # try converting list of lists to pandas dataframe
                try:
                    df = pd.DataFrame(rows[1:], columns=rows[0])
                except :
                    print(f"File '{self.container.path}' has unknown structure.")

                else:
                    table_dataframes.append(df)
            m += 1

        return table_dataframes

FileSystemCrawlerFactory.registerFileType(CSVcrawler, CSVcrawler.extension)

class PlainTextCrawler(Crawler):
    """
    Crawler for plain text files
    Also used as default general crawler if filetype-specific crawler is not registered
    """
    extension = "txt"
    def __init__(self, container):
        self.container = container
        # print(f"\tTXT crawler created for container #{self.container.id} '{self.container.name}' (file '{self.container.path}')")
        pass

    def crawl(self):
        """
        Do the crawl - go through the file and detect defined elements
        """
        print("No crawling procedure defined yet for Plain Text crawler")
        pass

FileSystemCrawlerFactory.registerFileType(PlainTextCrawler, PlainTextCrawler.extension)

