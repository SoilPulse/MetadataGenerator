# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests
#import base64

# start with a given DOI
#doi = "10.14454/FXWS-0523"
#doi = "10.5281/zenodo.6654150"
#doi = "10.5281/zenodo.10210062"
doi = "10.5281/zenodo.10209718"
#doi = "10.5281/zenodo.10210061"


def doi_ra(doi, meta=False):
    '''
    get registration agency from doi.org API
 
    Parameters
    ----------
    doi : string
        the DOI of a published dataset (10.XXX/XXXX).
    meta : bool
        return json instead of string of registration agency
    
    Returns
    -------
    information on Registration agency

    '''
    url_ra = "https://doi.org/ra/"+doi
    ra = requests.get(url_ra).json()
    if(meta):
        return(ra)
    else:
        return(ra[0]['RA'])
    
def test_doi_ra1():
    assert doi_ra("10.5281/zenodo.10209718") == "DataCite"

def test_doi_ra2():
    assert doi_ra("10.5281/zenodo.10209718", meta="True") == \
    [{'DOI': '10.5281/zenodo.10209718', 'RA': 'DataCite'}]


ra = doi_ra(doi)
print("DOI is registered at: "+ra)


def doi_meta(doi):
    '''
    Parameters
    ----------
    doi : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    ra = doi_ra(doi)
    if(ra == 'DataCite'):
        url = "https://api.datacite.org/dois/"+doi
        headers = {"accept": "application/vnd.api+json"}
        return(requests.get(url, headers=headers).json())
    else:
        return('Please contact admins, registration agency currently not covered')
    
meta_ra = doi_meta(doi)
print("Data was created by: "+str(meta_ra['data']['attributes']['creators']))
print("Data is titled: "+str(meta_ra['data']['attributes']['titles'][0]['title']))
print("Data can be retrieved at: "+str(meta_ra['data']['attributes']['url']))

#print(base64.b64decode(response['data']['attributes']['xml']))

def doi_data(doi):
    meta_ra = doi_meta(doi)
    dataset_url = meta_ra['data']['attributes']['url']
    if ("zenodo.org" in dataset_url):
        zenodo_id = dataset_url.split("/")[-1].split(".")[-1]
        print("retrieving information for Zenodo dataset: "+zenodo_id)
        
        response = requests.get("https://zenodo.org/api/deposit/depositions/"+zenodo_id+"/files").json()
        if (type(response) == dict):
            print("Data set can not be retrieved.")
        else:
            for file in response:
                if (".zip" in file['filename']):
                    print(file['filename'])
                print("Download-url: https://zenodo.org/records/"+zenodo_id+"/files/"+file['filename']+"?download=1")

doi_data(doi)
#    response = requests.get(https://zenodo.org/records/6654150/files/lenz2022.zip?download=1)
#    https://zenodo.org/api/deposit/depositions/6654150/files