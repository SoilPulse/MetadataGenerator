# -*- coding: utf-8 -*-
"""
Functions to retrieve metadata from data Hosters.

@author: Jonas Lenz
"""

import requests


def doi_ra(doi, meta=False):
    """
    Get registration agency from doi.org API.

    Parameters
    ----------
    doi : string
        the DOI of a published dataset (10.XXX/XXXX).
    meta : bool
        return json instead of string of registration agency

    Returns
    -------
    Information on Registration agency

    """
    try:
        url_ra = "https://doi.org/ra/"+doi
        ra = requests.get(url_ra).json()
        if (meta):
            return (ra)
        else:
            return (ra[0]['RA'])
    except Exception as ex:  # except if given string is not a DOI.
        return ("This is not a DOI. Error message: " + str(ex))


def doi_meta(doi):
    """
    Get metadata from registration agency for DOI.

    Parameters
    ----------
    doi : TYPE
        DESCRIPTION.

    Returns
    -------
    None.
    """
    ra = doi_ra(doi)
    if (ra == 'DataCite'):
        url = "https://api.datacite.org/dois/"+doi
        headers = {"accept": "application/vnd.api+json"}
        return (requests.get(url, headers=headers).json())
    else:
        return ('Please contact admins, registration agency \
               currently not covered')


def doi_files(doi):
    """
    List the files associated with the given DOI.

    Parameters
    ----------
    doi : String
        DOI to the original dataset.

    Returns
    -------
    List
        List of all Zip files associated with the dataset on Zenodo.

    """
    meta_ra = doi_meta(doi)
    dataset_url = meta_ra['data']['attributes']['url']
    if ("zenodo.org" in dataset_url):
        zenodo_id = dataset_url.split("/")[-1].split(".")[-1]
    #    print("retrieving information for Zenodo dataset: "+zenodo_id)
        response = requests.get("https://zenodo.org/api/deposit/depositions/"
                                + zenodo_id+"/files").json()
        if (type(response) == dict):
            print("Data set can not be retrieved.")
        else:
            file_list = []
            for file in response:
                if (".zip" in file['filename']):
                    file_list.append(
                        "https://zenodo.org/records/"+zenodo_id
                        + "/files/"+file['filename']+"?download=1"
                        )
        return (file_list)
    else:
        return ("Can not retrieve files. - This is currently implemented \
                ONLY for Zenodo.")
