# -*- coding: utf-8 -*-
"""
Tests for the web front end.

@author: Jonas Lenz
"""

from streamlit.testing.v1 import AppTest


class TestFrontend:
    dois = [
            "10.14454/FXWS-0523",
            "10.5281/zenodo.6654150",
            "10.5281/zenodo.10210062",
            "10.5281/zenodo.10209718",
            "10.5281/zenodo.10210061",
            ]
    app = "./src/webapp/streamlit.py"

    at = AppTest.from_file(app)
    at.run()

    def test_front(self):
        assert not self.at.exception

    def test_title(self):
        self.at.button[0].click().run()
        res = self.at.title[0].value
        assert res == "SoilPulse Metadata generator"

#    def test_get_ra(self):
#    """
#    Test is not working, understand how streamlit objects can be queried here.
#    """
#        self.at.button[0].click().run()
#        res = self.at.Element[0]
#        print(res)
#        assert res == "SoilPulse Metadata generator"
