import streamlit as st
from streamlit_modal import Modal

#import streamlit.components.v1 as components

# https://github.com/teamtv/streamlit_modal

modal = Modal(
    "Modify column",
    key="demo-modal",
    # Optional
    padding=10,    # default value
    max_width=844  # default value
)

open_modal = st.button("Add or modify column assignment")
if open_modal:
    modal.open()

if modal.is_open():
    colmet = {}
    with modal.container():
        action = st.radio("Action",
                          options=["split column",
                                   "attribute column"],
                          horizontal=True
                          )

        col = st.selectbox("Which Column", options=[1, 2, 3, 4])
        colmet[col] = {}
        if action == "split column":
            colmet[col]['sep'] = st.text_input("Split by")
            for side in ['left', 'right']:
                colmet[col][side] = {}
                colmet[col][side]['col'] = st.text_input("New "+side+" column")
                colmet[col][side]['agrovoc'] = st.text_input(
                    "Choose agrovoc concept", key="agro"+side)
                colmet[col][side]['unit'] = st.text_input(
                    "Select unit of measurement", key="unit"+side)


        if action == "attribute column":
            colmet[col]['agrovoc'] = st.text_input(
                "Choose agrovoc concept")
            colmet[col]['unit'] = st.text_input("Select unit of measurement")

        st.json(colmet)
