import streamlit as st

from pint import UnitRegistry
from astropy import units as u

# select all non-private attributes to get all available units
def vdir(obj):
    return [x for x in dir(obj) if not x.startswith('_')]



st.title("test PINT framework")

# invoke unit registry instance
ureg = UnitRegistry()

unitlist = vdir(ureg)

a = st.selectbox("all units Pint", options=unitlist)

q = ureg(a)
st.markdown(f"{q.units}", unsafe_allow_html=True)

unit = st.text_input("Unit", value="meter / kilogram * percent^2")

try:
    q = ureg(unit)
    st.write('The normal representation is {:}'.format(q))
    st.write('The pretty representation is {:~P}'.format(q))
    st.write('The HTML representation is {:~H}'.format(q))

#    st.write()
except Exception as e:
    st.warning(e)
    st.write("dont understand your unit")



st.title("Test Astropy")

unitlistastro = vdir(u)

astro = st.selectbox("all units Astropy", options=unitlistastro)

qastro = u.Unit(astro)
st.markdown(qastro)

unitastro = st.text_input("Unitastro", value="meter / kilogram * percent^2")

try:
    qastro = u.Unit(unitastro)
    st.write("written normal")
    st.write(qastro)
    st.write("written as SI")
    st.write(qastro.si)
except Exception as e:
    st.warning(e)
    st.write("dont understand your unit")
