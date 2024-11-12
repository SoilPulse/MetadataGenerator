# coding = utf-8
# -*- coding: utf-8 -*-

import os
import re
import csv
import io
import datetime
import tarfile
import zipfile
from collections import Counter
import chardet
import pandas as pd
import shutil
import copy

import pandas.errors
from frictionless import validate, formats
from frictionless.resources import Resource, TableResource, Package
from io import StringIO
# import magic


from ..project_management import ContainerHandler, ContainerHandlerFactory, Pointer, Crawler, CrawlerFactory
from ..db_access import EntityKeywordsDB
from .data_structures import TableContainer, ColumnContainer
# just for the standalone functions - will be changed
# from ..resource_management import *
import gzip



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

    return str(dialect.delimiter), str(dialect.lineterminator)

def is_file_archive(path):
    if os.path.isfile(path):
        path_split = path.split(".")
        if len(path_split) > 1:
            extension = path_split[-1]
            more_formats = ["gz", "rar"]
            if extension in get_shutil_archive_formats() or extension in more_formats:
                return True
            else:
                return False
        return False

def get_file_extension(path):
    if os.path.isdir(path):
        return None

    # remove empty parts of filename
    file_ext = [item for item in os.path.basename(path).split(".") if item]

    if len(file_ext) > 1:
        return file_ext[-1]
    else:
        return None

def get_shutil_archive_formats():
    """
    Return list of currently supported formats of shutil.unpack_archive() method.
    The extensions are stripped of the leading '.' so it can be compared to file extensions gained by .split('.')
    """
    archive_ext_list = []
    for format in shutil.get_unpack_formats():
        archive_ext_list.extend([ext.strip(".") for ext in format[1]])
    return archive_ext_list


class FileSystemContainer(ContainerHandler):
    containerType = 'filesystem'
    containerFormat = "File system"
    keywordsDBname = "keywords_filesystem"

    # dictionary of DB fields needed to save this subclass instance attributes
    DBfields = {"relative_path": "text"}
    # dictionary of attribute names to be used for DB save/update - current values need to be obtained at right time before saving
    serializationDict = {"relative_path": "rel_path"}

    @classmethod
    def getSpecializedSubclassType(cls, **kwargs):
        # if the container is loaded from the DB the 'type' attribute is already the specialized one
        if kwargs.get("type") is not None:
            return kwargs["type"]
        # otherwise it gets specialized here
        path = kwargs.get("path")
        if os.path.isfile(path):
            if is_file_archive(path):
                return "archive"
            else:
                return "file"
        elif os.path.isdir(path):
            return "directory"
        elif path is None:
            raise ValueError(f"'None' provided as path for FileSystemContainer creation..")
        else:
            raise ValueError(f"Provided path '{path}' is neither file nor directory.")


    def __init__(self, project_manager, parent_container, **kwargs):
        super().__init__(project_manager, parent_container, **kwargs)
        # file path relative to project temp directory
        self.path = kwargs["path"]
        self.rel_path = self.path.replace(project_manager.temp_dir+os.path.sep, "")
        self.project.containersOfPaths.update({self.rel_path: self.id})
        # get other useful properties of the file (size, date of creation ...)
        self.size = None

        if kwargs.get("date_created") is None:
            self.dateCreated = datetime.datetime.fromtimestamp(os.path.getctime(self.path)) if os.path.exists(self.path) else None
        else:
            self.dateCreated = kwargs.get("date_created")

        if kwargs.get("date_last_modified") is None:
            self.dateLastModified = datetime.datetime.fromtimestamp(os.path.getmtime(self.path)) if os.path.exists(self.path) else None
        else:
            self.dateLastModified = kwargs.get("date_last_modified")


    def showContents(self, depth=0, ind=". ", show_concepts=True, show_methods=True, show_units=True):
        """
        Prints structured info about the container and invokes showContents on all of its containers

        :param depth: current depth of showContent recursion
        :param ind: string of a single level indentation
        :param show_concepts: whether to show also the string-concepts translations
        :param show_methods: whether to show also the string-methods translations
        :param show_units: whether to show also the string-units translations
        """
        t = ind * depth
        dateFormat = "%d.%m.%Y"
        pContID = self.parentContainer.id if self.parentContainer is not None else "root"
        try:
            print(f"{t}{self.id} - {self.name} ({self.containerType}, {self.getFileSizeFormated()}, {self.dateCreated.strftime(dateFormat) }/{self.dateLastModified.strftime(dateFormat)}) [{len(self.containers)}]  >{pContID}")
        except AttributeError as e:
            print(f"{t}{self.id} - {self.name}")
        if show_concepts:
            if hasattr(self, "concepts"):
                print("  " * (depth + 1) + "concepts:") if len(self.concepts) > 0 else None
                for string, concepts in self.concepts.items():
                    add = "  " * (depth + 2) + string + ": "
                    i = 0
                    for conc in concepts:
                        if i > 0:
                            add += "; "
                        if conc.get('term'):
                            add += f"'{conc['term']}' "
                        if conc.get('locator'):
                            add += f"[{conc['locator']['start_char']}:{conc['locator']['end_char']}] "
                        add += f"{conc['uri']} ({conc['vocabulary']})"
                        i += 1
                    print(add)

        if show_methods:
            if hasattr(self, "methods"):
                print("  " * (depth + 1) + "methods:") if len(self.methods) > 0 else None
                for string, methods in self.methods.items():
                    print("  "*(depth+2)+string+": "+"; ".join([f"'{meth['uri']}' ({meth['vocabulary']})" for meth in methods]))

        if show_units:
            if hasattr(self, "units"):
                print("  " * (depth + 1) + "units:") if len(self.units) > 0 else None
                for string, units in self.units.items():
                    print("  "*(depth+2)+string+": "+"; ".join([f"'{unit['uri']}' ({unit['vocabulary']})" for unit in units]))

        # invoke showContents of sub-containers
        if len(self.containers) > 0:
            depth += 1
            for cont in self.containers:
                cont.showContents(depth, ind, show_concepts, show_methods, show_units)

    def getFileSize(self):
        return os.stat(self.path).st_size if os.path.isfile(self.path) else None

    def getFileSizeFormated(self):
        """Return a string of dynamically formatted file size."""
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

    def createTree(self, path, project_manager):
        tree = []
        for f in os.listdir(path):
            fullpath = os.path.join(path, f)
            new_container = project_manager.containerFactory.createHandler('filesystem', project_manager, self, name=f, path=fullpath)
            tree.append(new_container)
            project_manager.downloadedFiles.append(fullpath)
        return tree


    # def getSerializationDictionary(self):
    #     dict = super().getSerializationDictionary()
    #     for db_key, attr_key in self.serializationDict.items():
    #         dict.update({db_key: str(getattr(self, attr_key))})
    #     return dict

    def listOwnFiles(self, collection):
        collection.append(self.path)
        for cont in self.containers:
            cont.listOwnFiles(collection)
        return collection


ContainerHandlerFactory.registerContainerType(FileSystemContainer, FileSystemContainer.containerType)
EntityKeywordsDB.registerKeywordsDB(FileSystemContainer.containerType, FileSystemContainer.keywordsDBname)

class SingleFileContainer(FileSystemContainer):
    containerType = 'file'
    containerFormat = "File system single file"

    # dictionary of DB fields needed to save this subclass instance attributes
    DBfields = {"relative_path": "text",
                "date_created": "datetime",
                "date_last_modified": "datetime",
                "encoding": "text"}
    # dictionary of attribute names to be used for DB save/update - current values need to be obtained at right time before saving
    serializationDict = {"relative_path": "rel_path",
                         "date_created": "dateCreated",
                         "date_last_modified": "dateLastModified",
                         "encoding": "encoding"}

    def __init__(self, project_manager, parent_container, cascade=True, **kwargs):
        super().__init__(project_manager, parent_container, **kwargs)

        # get mime type of the file
        self.mimeType = self.getMimeType()
        # get other useful info of the file (size, date of creation ...)
        self.size = None
        self.fileExtension = get_file_extension(self.path)

        # load or detect encoding
        if kwargs.get("encoding") is None:
            self.encoding = detect_encoding(self.path)[0] if os.path.exists(self.path) else None
        else:
            self.encoding = kwargs.get("encoding")

        # get crawler - use loaded type if any
        if kwargs.get("crawler_type") is not None:
            # print(f"crawler_type: {kwargs.get('crawler_type')}")
            ctype = kwargs.get("crawler_type")
        # or pass the decision to general FileSystemCrawler
        else:
            ctype = 'filesystem'
        try:
            self.crawler = CrawlerFactory.createCrawler(ctype, self)
        except ValueError as e:
            print(e)
        else:
            if cascade:
                self.getAnalyzed(cascade=True)

        if not os.path.exists(self.path):
            print(f"\tfile of container '{self.name}' was not found.")

#        print(f"file {self.rel_path} has encoding: {self.encoding}")

    def createTree(self, *args):
        return []

    def getMimeType(self):
        # self.mimeType = magic.from_file(self.path)
        return

    def getAnalyzed(self, cascade=True, force=False, report=False):
        if super().getAnalyzed(cascade, force):
            if self.crawler:
                tables = self.crawler.analyze(report=report)
                if tables:
                    # print(f"tables:\n{tables}")
                    # print("\n\n")
                    self.containers = tables
                # print(f"table cont {self.id} containers: {self.containers}")

            for container in self.containers:
                container.getAnalyzed(cascade, force, report)
            self.wasAnalyzed = True

    def getCrawled(self, cascade=True, force=False, report=False):
        """
        Executes the routines for scanning, recognizing and extracting metadata (and maybe data)
        """
        if super().getCrawled(cascade, force):
            if self.crawler:
                self.crawler.crawl(report)

            if cascade:
                for container in self.containers:
                    container.getCrawled(cascade, force, report)

            self.wasCrawled = True
        return

ContainerHandlerFactory.registerContainerType(SingleFileContainer, SingleFileContainer.containerType)

class DirectoryContainer(FileSystemContainer):
    containerType = 'directory'
    containerFormat = "File system directory"

    def __init__(self, project_manager, parent_container, cascade=True, **kwargs):
        super().__init__(project_manager, parent_container, **kwargs)

        self.size = None

        if not os.path.exists(self.path):
            print(f"\tdirectory represented by container '{self.name}' was not found.")

        if cascade:
            self.containers = self.createTree(self.path, project_manager)

    def getAnalyzed(self, cascade=True, force=False, report=False):
        """
        Invokes getAnalyzed on all of his containers
        """

        if super().getAnalyzed(cascade, force):
            if cascade:
                for container in self.containers:
                    container.getAnalyzed(cascade, force, report)

            self.wasAnalyzed = True

        return

    def getCrawled(self, cascade=True, force=False, report=False):
        """
        Invokes getCrawled on all of his containers
        """

        if super().getCrawled(cascade, force):
            if cascade:
                for container in self.containers:
                    container.getCrawled(cascade, force, report)

            self.wasCrawled = True

        return


ContainerHandlerFactory.registerContainerType(DirectoryContainer, DirectoryContainer.containerType)


class ArchiveFileContainer(FileSystemContainer):
    containerType = 'archive'
    containerFormat = "File system archive file"

    # dictionary of DB fields needed to save this subclass instance attributes
    DBfields = {"relative_path": "text",
                "date_created": "datetime",
                "date_last_modified": None}
    # dictionary of attribute names to be used for DB save/update - current values need to be obtained at right time before saving
    serializationDict = {"relative_path": "rel_path",
                         "date_created": "dateCreated",
                         "date_last_modified": "dateLastModified"}
    def __init__(self, project_manager, parent_container, cascade=True, **kwargs):
        super().__init__(project_manager, parent_container, **kwargs)
        # get mime type of the file
        self.mimeType = self.getMimeType()
        # get other useful of the file (size, date of creation ...)
        self.size = None
        self.fileExtension = get_file_extension(self.path)

        if not os.path.exists(self.path):
            print(f"\tplaceholder directory of archive container '{self.name}' was not found.")

        # if os.path.exists(kwargs.get("path")) and os.path.isdir(kwargs.get("path")):
        #     # if the directory exists on the storage the archive is already unpacked
        #     print(f"my path: {kwargs.get('path')}")
        if cascade:
            # unpack and create the containers from content if not already on the storage
            self.containers = self.unpack(self.path, project_manager)


    def getMimeType(self):
        # self.mimeType = magic.from_file(self.path)
        return

    def listContents(self):
        """
        Lists the contents of the archive without unpacking it.

        :param archive_path: the source archive file
        :return: list of file names within the archive
        """
        contents = []
        try:
            if self.path.endswith(".zip"):
                with zipfile.ZipFile(self.path, 'r') as zip_ref:
                    contents = zip_ref.namelist()
            elif self.path.endswith(".tar.gz") or self.path.endswith(".tar"):
                with tarfile.open(self.path, 'r:*') as tar_ref:
                    contents = tar_ref.getnames()
            elif self.path.endswith(".gz") and not self.path.endswith(".tar.gz"):
                # For .gz files, we assume it's a single file inside
                contents = [os.path.basename(self.path).replace('.gz', '')]
            else:
                raise ValueError(f"Unsupported archive format: {self.path}")
        except OSError as err:
            print(f"Error reading '{self.path}': {err}")

        return contents

    def unpack(self, archive_path, project_manager, same_dir=False, target_dir=None, remove_archive=True):
        """
        Unpacks archive formats supported by shutil to a directory with the name of the archive
        Replaces all '.' with '_' in filename to derive a new directory name.

        :param archive_path: the source archive file
        :param project_manager: ProjectManager instance the containers belong to
        :param same_dir: the contents are unpacked into parent directory of the source archive file
        :param target_dir: output directory path, name of the archive with removed '.' is used instead if None
        :param remove_archive: whether to delete the source archive file after successful unpacking
        """
        output_tree = []
        # container name representing the original archive
        cont_name = os.path.basename(archive_path)

        if same_dir:
            #
            outDir = os.path.dirname(archive_path)
        else:
            # name of the directory that will be created to hold the contents instead of the original archive
            extractDirName = os.path.basename(archive_path).replace(".", "_")
            if target_dir is not None:
                outDir = target_dir
                extractDirName = os.path.basename(target_dir)
            else:
                outDir = os.path.join(os.path.dirname(archive_path), extractDirName)

        try:
            if archive_path.endswith(".gz") and not archive_path.endswith(".tar.gz"):

                if not os.path.exists(outDir):
                    os.makedirs(outDir)
                # just remove the ending ".gz"
                filename = ".".join(cont_name.split(".")[:-1])
                out_path = os.path.join(outDir, filename)

                print(f"Extracting '{os.path.basename(archive_path)}' to '{out_path}'")

                with gzip.open(archive_path, 'rb') as f_in:
                    with open(out_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                self.path = out_path
                self.rel_path = out_path.replace(project_manager.temp_dir, "").strip("\\/ ")

                output_tree = self.createTree(outDir, project_manager)

            elif archive_path.endswith(".tar.gz"):
                print(f"Extracting '{os.path.basename(archive_path)}' to '{outDir}'")
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(path=outDir)
                self.path = outDir
                self.rel_path = outDir.replace(project_manager.temp_dir, "").strip("\\/ ")
                output_tree = self.createTree(outDir, project_manager)

            elif archive_path.endswith(".rar"):
                print(f"RAR archives not implemented yet '{os.path.basename(archive_path)}' to '{outDir}'")
                remove_archive = False
                self.path = archive_path
            else:
                # all other archive types
                print(f"Extracting '{os.path.basename(archive_path)}' to '{outDir}'")
                shutil.unpack_archive(archive_path, outDir)
                self.path = outDir
                self.rel_path = extractDirName
                output_tree = self.createTree(outDir, project_manager)

        except OSError as err:
            print(f"File '{archive_path}' couldn't be extracted. It is not a valid archive or the file is corrupted.")
            print(err)
        else:
            if remove_archive:
                try:
                    os.remove(archive_path)
                except OSError:
                    print(f"\nFile '{archive_path}' couldn't be deleted. It may be locked by another application.")

        project_manager.downloadedFiles.append(self.path)
        return output_tree


    def getCrawled(self, cascade=True, force=False):
        """
        Executes the routines for scanning, recognizing and extracting metadata (and maybe data)
        """
        for container in self.containers:
            container.getCrawled()

ContainerHandlerFactory.registerContainerType(ArchiveFileContainer, ArchiveFileContainer.containerType)

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

# class FileSystemCrawlerFactory:
#     """
#     File system type crawler factory
#     """
#
#     # directory of registered publisher types classes
#     filetypes = {}
#
#     # the one and only instance
#     _instance = None
#
#     @classmethod
#     def registerFileType(cls, file_type_crawler_class):
#         cls.filetypes[file_type_crawler_class.extension] = file_type_crawler_class
#         print(f"Crawler for file type '{file_type_crawler_class.extension}' registered.")
#         return
#
#     @classmethod
#     def createCrawler(cls, file_extension, container, *args):
#         """
#         Creates and returns instance of ContainerHandler for the file container provided
#         """
#
#         if file_extension:
#             if file_extension.lower() not in cls.filetypes.keys():
#                 filetypes = ",".join(["'" + k + "'" for k in cls.filetypes.keys()])
#                 print(
#                     f"\t{os.path.basename(container.path)} - unsupported Crawler subclass type '{file_extension.lower()}' (registered types are: {filetypes}) - plain text crawler will be used instead.")
#
#                 return cls.filetypes['txt'](container, *args)
#             else:
#                 # special handling of different file types can be added here ...
#                 if container.fileExtension == 'txt':
#                     # ... like trying csv crawler on txt file
#                     # print("\t\ttrying csv crawler on txt file")
#                     output_crawler = cls.filetypes['csv'](container, *args)
#                     # validate usability of CSV crawler
#                     if output_crawler.validate():
#                         print(f"\tCSV structure was detected in {container.path} and will be treated as such.")
#                         return output_crawler
#                     # otherwise just use native txt crawler
#                     else:
#                         # print("\t\t==> just text")
#                         return cls.filetypes[file_extension](container, *args)
#                 else:
#                     return cls.filetypes[file_extension](container, *args)
#         else:
#             print(f"\tFile has no extension - plain text crawler will be used instead.")
#             return cls.filetypes['txt'](container, *args)
#
#     def __init__(self):
#         pass

class FileSystemCrawler(Crawler):
    crawlerType = 'filesystem'

    @classmethod
    def getSpecializedCrawlerType(cls, container, **kwargs):
        if not hasattr(container, "fileExtension"):
            print(f"\nContainer without fileExtension attribute was passed to 'filesystem' Crawler.\n"
                  f"'zero' crawler will be assigned instead.")
            return "zero"
        else:
            # special handling of different file types can be added here ...
            if container.fileExtension == 'txt':
                # ... like trying csv crawler on txt file
                return "csv"
            else:
                return container.fileExtension

    @classmethod
    def getFallbackCrawlerType(cls, container, **kwargs):
        if not hasattr(container, "fileExtension"):
            print(f"\nContainer without fileExtension attribute was passed to 'filesystem' Crawler.\n"
                  f"'zero' crawler will be assigned instead.")
            return "zero"
        else:
            return container.fileExtension

CrawlerFactory.registerCrawlerType(FileSystemCrawler)

class CSVcrawler(Crawler):
    """
    Crawler for CSV files
    """

    crawlerType = "csv"

    @classmethod
    def getSpecializedCrawlerType(cls, container, **kwargs):
        return cls.crawlerType
    @classmethod
    def getFallbackCrawlerType(cls, container, **kwargs):
        return PlainTextCrawler.crawlerType

    def __init__(self, container):
        super().__init__(container)

        self.cell_sep = None
        self.line_sep = None

    def validate(self):
        return validate(self.container.path)

    def get_frictionless_resource(self):
        print(f"\ncreating CSV resource for '{self.container.path}' of container #{self.container.id},"
              f" encoding '{self.container.encoding}'")

        # if the container was not analyzed for any reasons it doesn't have cell_sep attribute yet
        if not hasattr(self, "cell_sep") or not hasattr(self, "line_sep"):
            self.find_delimiters()
        if self.cell_sep is not None:
            control = formats.CsvControl(delimiter=self.cell_sep, skip_initial_space=True)
        else:
            control = formats.CsvControl(skip_initial_space=True)
        resource = Resource(path=self.container.path, format='csv', control=control, encoding=self.container.encoding)
        resource.infer()


        print(f"container #{self.container.id}:\n{resource}")
        return resource

    def find_delimiters(self):
        # read the file into a text
        with open(self.container.path, 'r', encoding=self.container.encoding) as file:
            try:
                # read only first x characters to avoid reading big files
                content = file.read(2000)
            except UnicodeDecodeError as e:
                print(f"Content of container '{self.container.name}' couldn't be analyzed due to encoding issues.")
            else:
                try:
                    self.cell_sep, self.line_sep = detect_delimiters(content)
                except:
                    print(f"Searching for delimiters in container {self.container.name} failed.")
                    self.cell_sep = None
                    self.line_sep = None

    def analyze(self, report=False):
        print(f"\nanalyzing CSV '{self.container.path}' of container #{self.container.id}, "
            f"encoding '{self.container.encoding}'") if report else None
        # find delimiters and encoding
        self.find_delimiters()
        if self.cell_sep is not None:
            tables = self.find_tables(3, report)
            if tables is None:
                print(f"\tcontainer {self.container.id} couldn't be properly analyzed")
                return
            if len(tables) == 0:
                print(f"\tfound no understandable tables") if report else None
                return None
            else:
                print(
                    f"\tfound {len(tables)} understandable table structure{'s' if len(tables) > 1 else ''}") if report else None
                table_conts = []
                i = 1
                for tab in tables:
                    # get rid of the file extension
                    name = ".".join(os.path.basename(self.container.path).split(".")[:-1])
                    # append table index if there are more tables in the file
                    name += f"_{i}" if len(tables) > 1 else ""
                    # assign the container name as resource name as well
                    tab.name = name
                    # create new TableContainer from the table
                    cont_args = {"name": name,
                                 "fl_resource": tab,
                                 "pd_dataframe": None}
                    newCont = self.container.project.containerFactory.createHandler("table", self.container.project,
                                                                                    self.container, **cont_args)
                    table_conts.append(newCont)

                    # print(newCont.fl_resource.schema)
                    i += 1
                # change flag of parent container
                self.container.isAnalyzed = True

                return table_conts
        print(f"\tcell separator was not found. The file content is probably not a table.") if report else None
        return None

    def crawl(self, report=True):
        """
        Do the crawl - go through the container and detect defined elements
        The results of the crawl are directly assigned to crawler's parent container attributes

        :return:
        """

        print(f"crawling CSV '{self.container.path}' of container #{self.container.id}, encoding '{self.container.encoding}'") if report else None
        # # search for string to concept translations
        # self.container.concepts = self.find_translations(self.container.project.globalConceptsVocabulary)
        # print(f"concept translations:\n{self.container.concepts}")
        # # search for string to method translations
        # self.container.methods = self.find_translations(self.container.project.globalMethodsVocabulary)
        # # search for string to unit translations
        # self.container.units = self.find_translations(self.container.project.globalUnitsVocabulary)

        return

    def split_into_chunks(self, content, cell_sep, line_sep="\n"):
        """
        Splits the content into chunks where each chunk is separated by:
        - At least one newline, followed by either:
          - Another newline, or
          - Any sequence of blank characters, cell delimiter characters, and newlines.

        :param content: The raw text of the CSV file.
        :param cell_delimiters: A string containing cell delimiter characters (e.g., ';,').
        :return: A list of content chunks.
        """
        if cell_sep is not None:
            # Define pattern to capture table breaks based on specific newline and delimiter structure
            pattern = rf'({line_sep}{{2,}})|({line_sep}[{re.escape(cell_sep)}\s]*{line_sep})'
            # print(f"Regex pattern used for splitting: {pattern}\n")
            #
            # # Previewing content for debugging
            # print(f"Content preview with indexes:")
            # for i, char in enumerate(content[:200]):
            #     print(f"{i}: '{char}'", end=", " if (i + 1) % 10 != 0 else "\n")

            # Confirm pattern matches
            matches = re.finditer(pattern, content)
            found = False
            for i, match in enumerate(matches, 1):
                found = True
                print(f"Match {i}: '{match.group()}' at position {match.start()}-{match.end()}")
            if not found:
                # print("No signs of multiple tables found.\n")
                return None

            # Split the content based on the pattern
            chunks = re.split(pattern, content)

            # Remove empty chunks and strip extra spaces/newlines from each chunk
            return [chunk.strip() for chunk in chunks if chunk.strip()]
        else:
            return None

    def find_tables(self, min_lines=3, report = True):
        """
        Searches for coherent tables by regular expression.
        Returns frictionless TableResource objects of all tables found in the file.

        :param min_lines: number of consistent lines needed for table identification
        :return: list of TableResource objects (even for a single table)
        """

        # read the file into a text
        with open(self.container.path, 'r', encoding=self.container.encoding) as file:
            try:
                content = file.read()
            except UnicodeDecodeError as e:
                print(f"Container '{self.container.name}' couldn't be analyzed due to encoding issues.")
                return []

        if hasattr(self, "cell_sep"):
            if self.cell_sep is not None:
                # try to split content into multiple tables
                table_segments = self.split_into_chunks(content, self.cell_sep, self.line_sep)
                # create more tables from the content if found
                if table_segments is not None:
                    resources = self.create_tables_from_segments(table_segments)
                    return resources

                # or use the whole file for resource creation
                else:
                    # print(f"container path: {self.container.path}")
                    # create the resource from parent container file
                    # check the file structure
                    # - .validate() does not work properly because of wrong field type casting
                    # - .describe() is used instead which has better guesses on the fields schema
                    try:
                        report = Resource.describe(os.path.normpath(self.container.path), format="csv", encoding=self.container.encoding)
                    except Exception as e:
                        print(f"frictionless.Resource.describe() failed for file '{self.container.path}':", e)
                        return None

                    # create the control object for frictionless resource creation
                    control = formats.CsvControl(skip_initial_space=True)
                    # set cell delimiter by crawler delimiter if not None
                    if self.cell_sep is not None:
                        control.delimiter = self.cell_sep

                    resource = TableResource(path=os.path.normpath(self.container.path),
                                             scheme='file',
                                             format='csv',
                                             encoding=self.container.encoding,
                                             control=control)
                    resource.infer()
                    # print(f"resource: {resource}")

                    # workaround to recognize a valid table even if the .validate() would produce false
                    if len(resource.schema.fields) > 0:
                        # set resource encoding by container encoding if not None
                        if self.container.encoding is not None:
                            resource.encoding = self.container.encoding
                        return [resource]

        return None
        # """
        # Searches for coherent tables by regular expression.
        # Returns frictionless TableResource objects of all tables found in the file.
        #
        # :param min_lines: number of consistent lines needed for table identification
        # :return: list of TableResource objects (even for a single table)
        # """
        #
        # encoding = self.container.encoding
        #
        # # read the file into a text
        # with open(self.container.path, 'r', encoding=encoding) as file:
        #     try:
        #         content = file.read()
        #     except UnicodeDecodeError as e:
        #         print(f"container '{self.container.name}' couldn't be analyzed due to problems with encoding.")
        #         print(self.container.path)
        #         return []
        #     else:
        #         # try detecting delimiters from file content
        #         try:
        #             cell_sep, line_sep = detect_delimiters(content)
        #         except:
        #             return []
        #         print(f"\tcell delimiter: '{cell_sep}'") if report else None
        #
        #         # pattern to match CSV-like tables without knowing delimiters
        #         pattern = r'(?:(?<!\w)[^\w\s]*(?:\w+\W*(?:\w+\W*)+\w+|\w+(?:\W+\w+)+\w+)\b(?:\W|\Z))'
        #         # pattern = r'(?:(?<!\w)[^\w\s]*(?:\w+\W*(?:\w+\W*)+\w+|\w+(?:\W+\w+)+\w+)\b(?:\W|$))(?!\n\s*$)'
        #         # pattern = r'(?:(?<!\w)[^\w\s]*(?:\w+\W*(?:\w+\W*)+\w+|\w+(?:\W+\w+)+\w+)\b(?:\W|$))(?=\n|\Z)'
        #
        #         # find all matches and their start character and length
        #         matches = re.finditer(pattern, content)
        #         # filter matches based on structure (e.g., number of lines) and store start character and length
        #
        #         # the file is directly converted to TableResource if only one table is found in the file
        #         num_matches = sum(1 for _ in matches)
        #         if num_matches == 1:
        #             try:
        #                 if cell_sep is not None:
        #                     control = formats.CsvControl(
        #                         delimiter=cell_sep,  # Single space as the delimiter
        #                         # quote_char='"',  # Fields are wrapped in double quotes
        #                         skip_initial_space=True  # Ignore multiple spaces between fields
        #                     )
        #
        #                     fl = TableResource(self.container.path, format='csv', encoding=encoding, control=control)
        #
        #
        #                 else:
        #                     fl = TableResource(self.container.path, format='csv', encoding=encoding)
        #                 # infer the columns scheme for frictionless resource
        #                 fl.infer()
        #                 pd = pandas.read_csv(self.container.path, encoding=encoding, on_bad_lines='skip')
        #                 return [[fl, pd]]
        #             except pandas.errors.ParserError as e:
        #                 print(
        #                     f"Table '{self.container.path}' couldn't be parsed to pandas dataframe")
        #                 return []
        #         else:
        #             tables = []
        #             m = 0
        #             for match in matches:
        #                 start_char = match.start()
        #                 length = match.end() - match.start()
        #
        #                 # split the content based on provided index pairs
        #                 segment = content[match.start():match.end()]
        #
        #                 # create new TableResource from the data segment
        #                 resource = TableResource(data=StringIO(segment), format='csv')
        #                 # create new DataFrame  from the data segment
        #                 try:
        #                     dataframe = pandas.read_csv(StringIO(segment), encoding=encoding, on_bad_lines='skip')
        #                 except pandas.errors.ParserError as e:
        #                     print(f"Error while trying to create pandas frame from table {m} of {num_matches} in '{self.container.path}'")
        #                     print(e.message)
        #                 tables.append([resource, dataframe])
        #
        #             return tables

    def create_tables_from_segments(self, segments):
        # for now raise an error
        raise NotImplementedError("Spliting single csv file into multiple tables is not implemented yet.")
        # solve the spliting in the future ...
        tables = []
        i = 1
        for segment in segments:
            # Create a TableResource and pandas DataFrame for each table segment
            try:
                control = formats.CsvControl(skip_initial_space=True)
                # set cell delimiter by crawler delimiter if not None
                if self.cell_sep is not None:
                    control.delimiter = self.cell_sep

                # wrap the segment in StringIO to simulate a file-like object
                segment_io = StringIO(segment)
                segment_io.name = self.container.path

                resource = TableResource(data=segment_io,
                                         scheme="text",
                                         format='csv',
                                         control=control)

                # run validation without type checks
                # report = resource.validate()

                report = resource.describe()
                print(f"resource.describe():\n{report}")

                if len(report.scheme) > 0:
                    # set resource encoding by container encoding if not None
                    if self.container.encoding is not None:
                        resource.encoding = self.container.encoding

                    resource.infer()

                    dataframe = pd.read_csv(segment_io,
                                            delimiter=self.cell_sep,
                                            encoding=self.container.encoding,
                                            on_bad_lines='skip')

                    tables.append([resource, dataframe])
                else:
                    print(f"\tfound segment {i} is not a valid table structure")
                    if report:
                        print(f"{segment}\n{40 * '='}\n{resource.validate()}")
                        num_type_errors = 0
                        for task in report.tasks:
                            for error in task['errors']:
                                if error['type'] == "type-error":
                                    num_type_errors += 1
                        print(f"total number of errors: {report['stats']['errors']}")
                        print(f"number of type errors: {num_type_errors}")
            except pd.errors.ParserError as e:
                print(f"Error parsing table to pandas dataframe: {e}")
            i += 1
        return tables

CrawlerFactory.registerCrawlerType(CSVcrawler)
# FileSystemCrawlerFactory.registerFileType(CSVcrawler)

class PlainTextCrawler(Crawler):
    """
    Crawler for plain text files
    Also used as default general crawler if filetype-specific crawler is not registered
    """
    crawlerType = "txt"

    @classmethod
    def getSpecializedCrawlerType(cls, container, **kwargs):
        return cls.crawlerType

    @classmethod
    def getFallbackCrawlerType(cls, container, **kwargs):
        return Crawler.crawlerType

    def __init__(self, container):
        super().__init__(container)
        # print(f"\tTXT crawler created for container #{self.container.id} '{self.container.name}' (file '{self.container.path}')")

CrawlerFactory.registerCrawlerType(PlainTextCrawler)


# FileSystemCrawlerFactory.registerFileType(PlainTextCrawler)

