# coding = utf-8
# -*- coding: utf-8 -*-

import os
from src.soilpulse.resource_management import DatasetHandler, DatasetHandlerFactory, Pointer, Crawler

# just for the standalone functions - will be changed
from src.soilpulse.resource_management import *


class FileSystemDataset(DatasetHandler):
    datasetFormat = "File system"
    def __init__(self, name, downloadDir, doi=None):
        super(FileSystemDataset, self).__init__(name, doi)
        # list of all the directories that belong to the repository
        self.directories = []
        # list of all the files that belong to the repository
        self.sourceURLs = []
        # directory where the script will have access to write
        self.downloadDir = downloadDir

        if doi:
            URLlist = getFileListOfDOI(doi)
            self.sourceURLs.extend(URLlist)
            self.downloadFiles(URLlist, self.downloadDir, True)

    def downloadFiles(self, url_list, target_dir, unzip=True):
        """
        Download files from url list and unzips zip files.

        :param url_list: list of urls to be downloaded
        :param target_dir: local directory that will be used to download and optionally extract archives
        :param unzip: if the downloaded file is a .zip archive it will be extracted if unzip=True

        :return: dictionary of file types for input URLs
        """
        # create the target directory if not exists
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

        result = {}
        for url in url_list:
            url_host = "/".join(url.split("/")[0:3])
            file_name = url.split("/")[-1].split("?")[0]
            print("downloading file '{}' from {}.".format(file_name, url_host))
            local_file_path = os.path.join(target_dir, file_name)
            try:
                response = requests.get(url, params={"download": "1"})
            except requests.exceptions.ConnectionError:
                print("\t\tA connection error occurred. Check your internet connection.")
                return False
            except requests.exceptions.Timeout:
                print("\t\tThe request timed out.")
                return False
            except requests.exceptions.HTTPError as e:
                print("\t\tHTTP Error:", e)
                return False
            except requests.exceptions.RequestException as e:
                print("\t\tAn error occurred:", e)
                return False
            else:
                # the parameter download = 1 is specific to Zenodo
                if response.ok:
                    with open(local_file_path, mode="wb") as filesave:
                        filesave.write(response.content)
                else:
                    # something needs to be done if the response is not OK ...
                    print("\t\tThe response was not OK!")
                    return False

                if (file_name.endswith(".zip") and unzip):
                    self.extractZipFile(local_file_path)
                    result[url] = "unzipped zip file"
                else:
                    result[url] = "raw file"
        print("\t... successful")
        return result

    def extractZipFile(self, theZip):
        from zipfile import ZipFile

        try:
            print("extracting '{}'".format(theZip))
            with ZipFile(theZip) as my_zip_file:
                my_zip_file.extractall(os.path.dirname(theZip))
        except ZipFile.BadZipfile:
            print("File '{}' is not a valid ZIP archive and couldn't be extracted".format(theZip))
        else:
            try:
                os.remove(theZip)
            except OSError:
                print("\nFile '{}' couldn't be deleted. It may be locked by another application.".format(theZip))

    def showContents(self):
        print("{}:".format(self.name))
        print(self.sourceURLs)

    def unzipToDir(self, zipfile, targetDir):

        return

    def scanFileStructure(self, directory):
        """
        scans a parent directory to fill inner properties
        """
        return

DatasetHandlerFactory.registerDatasetType(FileSystemDataset, "filesystem")

class FileSystemPointer(Pointer):
    def __init__(self, filename, start, length):
        # full path to the file of appearance
        self.filename = filename
        # index of place where the value starts
        self.start = start
        # length of the value in characters
        self.length = length
        pass

    pass


class FilesystemCrawler(Crawler):
    """
    Crawler for file system repositories
    """

    pass
