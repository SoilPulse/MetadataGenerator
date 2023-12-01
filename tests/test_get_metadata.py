# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from scripts.get_metadata import *

# start with a given DOI
#doi = "10.14454/FXWS-0523"
#doi = "10.5281/zenodo.6654150"
#doi = "10.5281/zenodo.10210062"
#doi = "10.5281/zenodo.10209718"
#doi = "10.5281/zenodo.10210061"

def test_doi_ra1():
    assert doi_ra("10.5281/zenodo.10209718") == "DataCite"

def test_doi_ra2():
    assert doi_ra("10.5281/zenodo.10209718", meta="True") == \
    [{'DOI': '10.5281/zenodo.10209718', 'RA': 'DataCite'}]
