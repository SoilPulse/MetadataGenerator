# Application examples


## SWIG data

[The Soil Water Infiltration Global database 10.1594/PANGAEA.885492](https://doi.pangaea.de/10.1594/PANGAEA.885492)
includes data in tabular form in csv files and alternatively in a single multi sheet xlsx.

The structure of this dataset was actually to complex to be readily transformed within SoilPulse:
 - SWIG has one table file per concept (time, infiltration volume)
 - In those on column per experiment (column name identifies experiment)
 - Concepts are so assigned by file name, not column header.
 - Primary key consits of Experiment ID in column header and time step by the position within the column

 - The frictionless transformation step.table_melt() should be able to resolve this structure, but prooved to be very resource intensive for >5000 columns
 - Correct joining of time with infiltration_volume could not be realized by now (position within sheet references from on table to the other)
