# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from soilpulsecore import get_metadata as gm


class TestGetMetadata:
    dois = [
            "10.14454/FXWS-0523",
            "10.5281/zenodo.6654150",
            "10.5281/zenodo.10210062",
            "10.5281/zenodo.10209718",
            "10.5281/zenodo.10210061",
            ]

    def test_doi_ra_one(self):
        assert gm.doi_ra(self.dois[3]) == "DataCite"

    def test_doi_ra_two(self):
        assert gm.doi_ra(self.dois[3], meta="True") == \
            [{'DOI': '10.5281/zenodo.10209718', 'RA': 'DataCite'}]

    def test_doi_ra_three(self):
        assert gm.doi_ra("notaDOI") == \
            "This is not a DOI. Error message: 'RA'"

    def test_doi_files_one(self):
        assert gm.doi_files(self.dois[3]) == \
            ['https://zenodo.org/records/10209718/files/Raman.zip?download=1',
             'https://zenodo.org/records/10209718/files/Optical images.zip?download=1',
             'https://zenodo.org/records/10209718/files/TGA.zip?download=1',
             'https://zenodo.org/records/10209718/files/XRD.zip?download=1',
             'https://zenodo.org/records/10209718/files/Auger.zip?download=1',
             'https://zenodo.org/records/10209718/files/Figures.zip?download=1',
             'https://zenodo.org/records/10209718/files/SEM.zip?download=1',
             'https://zenodo.org/records/10209718/files/Video-PLD.zip?download=1']

    def test_doi_files_two(self):
        assert gm.doi_files(self.dois[2]) == \
            ['https://zenodo.org/records/10210062/files/zenodo_data.zip?download=1']
