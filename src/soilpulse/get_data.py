# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 09:35:03 2023.

@author: Jonas Lenz
"""

# from io import BytesIO
import requests
import os


def download_data(URL, file_list, target_dir, autounzip=True):
    """Download files from url list and unzips zip files."""
    result = {}
    for file in file_list:
        file_url = str(URL + file)
        response = requests.get(file_url, params={"download": "1"})
        # the parameter download = 1 is speciic to Zenodo
        if response.ok:
            with open(target_dir+file,
                      mode="wb") as filesave:
                filesave.write(response.content)
        if (".zip" in file and autounzip):
            from zipfile import ZipFile
            with ZipFile(target_dir+file) as my_zip_file:
                my_zip_file.extractall(target_dir)
            os.remove(target_dir+file)
            result[file_url] = "unzipped zip file"
        else:
            result[file_url] = "raw file"
    return result
# Do also a hash checkup, if hash values are given by data hoster!
