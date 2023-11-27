# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests

# start with a given DOI
#doi = "10.14454/FXWS-0523"
doi = "10.5281/zenodo.6654150"
doi = "10.5281/zenodo.10210062"
#doi = "10.5281/zenodo.10209718"
#doi = "10.5281/zenodo.10210061"


# get registration agency from doi.org API
# query doi.org
url_ra = "https://doi.org/ra/"+doi
ab = requests.get(url_ra).json()

# get RA
abc = ab[0]
ra = abc['RA']

if(ra == 'DataCite'):
    url = "https://api.datacite.org/dois/"+doi
    headers = {"accept": "application/vnd.api+json"}
    response = requests.get(url, headers=headers).json()
    print(response['data']['attributes']['creators'])
    print(response['data']['attributes']['titles'])
    dataset_url = response['data']['attributes']['url']
    print(dataset_url)
    
else:
    print('Please contact admins, registration agency currently not covered')
    
if ("zenodo.org" in dataset_url):
    zenodo_id = dataset_url.split("/")[-1].split(".")[-1]
    print(zenodo_id)
    
    response = requests.get("https://zenodo.org/api/deposit/depositions/"+zenodo_id+"/files").json()
    if (type(response) == dict):
        print("Data set can not be retrieved.")
    else:
        for file in response:
            if (".zip" in file['filename']):
                print(file['filename'])
            print("Download-url: https://zenodo.org/records/"+zenodo_id+"/files/"+file['filename']+"?download=1")


#    response = requests.get(https://zenodo.org/records/6654150/files/lenz2022.zip?download=1)
#    https://zenodo.org/api/deposit/depositions/6654150/files