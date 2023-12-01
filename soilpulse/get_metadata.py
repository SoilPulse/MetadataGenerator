# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests

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
