# LIB-AV-ingestprep

A python script that automates digital preservation workflows in Emory Libraries Media Preservation.  

The script performs the following pre-ingest tasks for audiovisual material intended for the Interim Storage Repository (LIB-AV): 
- copy files to a staging directory
- get mediainfo metadata from files
- move files to the top level of the directory
- renames files and staging directory according to the LIB-AV naming convention
- prepares and arranges an ingest csv

Bits and pieces adapted from [IFIscripts](https://github.com/Irish-Film-Institute/IFIscripts).
