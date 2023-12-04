# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from soilpulse import get_metadata

# start with a given DOI
#doi = "10.14454/FXWS-0523"
#doi = "10.5281/zenodo.6654150"
#doi = "10.5281/zenodo.10210062"
#doi = "10.5281/zenodo.10209718"
#doi = "10.5281/zenodo.10210061"

class TestGetMetadata:
    doi = "10.5281/zenodo.10209718"

    def test_doi_ra_one(self):
        assert get_metadata.doi_ra(self.doi) == "DataCite"

    def test_doi_ra_two(self):
        assert get_metadata.doi_ra(self.doi, meta="True") == \
            [{'DOI': '10.5281/zenodo.10209718', 'RA': 'DataCite'}]

    def test_doi_ra_three(self):
        assert get_metadata.doi_ra("notaDOI") == "This is not a DOI."