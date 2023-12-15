# -*- coding: utf-8 -*-
"""
Frontend implementation for the SoilPulse Metadata Generator.

Makes use of st.session_state - see this guide:
https://gist.github.com/asehmi/f7e35c3880897fbae92adc7a5315ac0e
It pickles to cache metadata.

@author: Jonas Lenz
"""

import streamlit as st

st.title("Welcome to SoilPulse!")

st.write("SoilPulse allows you to create and maintain metadata for your\
         dataset, so it can be made machine readable. --> See Generator")
st.write("You can also explore and query all datasets, which are made machine\
         readable through SoilPulse. --> See Explorer")
