# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 09:35:03 2023.

@author: Jonas Lenz
"""

# from io import BytesIO
import requests
# from zipfile import ZipFile
# from urllib.request import urlopen
from soilpulse import get_metadata as gm

# def load_data(url):
#    f = urlopen(url)

#    with ZipFile(BytesIO(f.read())) as my_zip_file:
#        for contained_file in my_zip_file.namelist():
#            st.write(contained_file)
#            if (contained_file.endswith("README.md")):
#            with open(("unzipped_and_read_" + contained_file + ".file"),
#               "wb") as output:
#                st.header("accesing README")
#                for line in my_zip_file.open(contained_file).readlines():
#                    st.write(line)


def url_data(url):
    """
    .

    Parameters
    ----------
    url : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    print("Download-url: "+url)
    return None


def path_data(path):
    """
    .

    Parameters
    ----------
    path : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    print("Linking SoilPulse to: "+path)
    return None


def data_files(path):
    """
    .

    Parameters
    ----------
    path : TYPE
        DESCRIPTION.

    Returns
    -------
    files : TYPE
        DESCRIPTION.

    """
    files = ['list', 'of', 'all', 'files', 'in', 'the', 'dir']
    return files


def doi_data(doi):
    """
    .

    Parameters
    ----------
    doi : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    meta_ra = gm.doi_meta(doi)
    dataset_url = meta_ra['data']['attributes']['url']
    if ("zenodo.org" in dataset_url):
        zenodo_id = dataset_url.split("/")[-1].split(".")[-1]
        print("retrieving information for Zenodo dataset: "+zenodo_id)

        response = requests.get("https://zenodo.org/api/deposit/depositions/"
                                + zenodo_id+"/files").json()
        if (type(response) == dict):
            print("Data set can not be retrieved.")
        else:
            for file in response:
                if (".zip" in file['filename']):
                    print(file['filename'])
                print("Download-url: https://zenodo.org/records/"+zenodo_id
                      + "/files/"+file['filename']+"?download=1")
    else:
        print("Can not retrieve files. - This is currently implemented \
              ONLY for Zenodo.")
