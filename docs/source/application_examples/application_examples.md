# Application examples

## [TUBAF data](#tubaf) 

The data from several experimental campaigns of the [TU Bergakademie Freiberg (TUBAF)](https://tu-freiberg.de/fakult3/ibf/bodenphysik-und-oekohydrologie) was curated within a dissertation thesis and is available in differing data structures from the zenodo publication [10.5281/zenodo.6654150](https://doi.org/10.5281/zenodo.6654150).

- One structure holds the relevant data in tabular form, within three tables
- Units, methods and concepts were manually assigned
- A pipeline was manually created to transform the data in a machine readable data structure

## [Ries data](#ries)

[Ries et. al.](https://doi.org/10.6094/UNIFR/151460) data contains data of a experimental campaign on 21 experimental sites with 6 distinct experiments on each site.
The data is published in an institutional repository, without table descriptive metadata interpreted by this repository.
Metadata for each table column is contained within the data *.tsv files in comment rows, which were extracted and parsed to fricitonless descriptors.
Concepts from controlled vacabularies were assigned to the fricitonless descriptor from a user defined mapping.


## [SWIG data](#swig)

[The Soil Water Infiltration Global database 10.1594/PANGAEA.885492](https://doi.pangaea.de/10.1594/PANGAEA.885492)
includes data in tabular form in csv files and alternatively in a single multi sheet xlsx.

The structure of this dataset was actually to complex to be readily transformed within SoilPulse:
 - SWIG has one table file per concept (time, infiltration volume)
 - In those on column per experiment (column name identifies experiment)
 - Concepts are so assigned by file name, not column header.
 - Primary key consits of Experiment ID in column header and time step by the position within the column

 - The frictionless transformation step.table_melt() should be able to resolve this structure, but prooved to be very resource intensive for >5000 columns
 - Correct joining of time with infiltration_volume could not be realized by now (position within sheet references from on table to the other)
