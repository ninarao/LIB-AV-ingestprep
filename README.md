# LIB-AV-ingestprep

Python scripts that automate digital preservation workflows in Emory Libraries Media Preservation.  

`prepforlibav.py` performs the following pre-ingest tasks for audiovisual material intended for the Interim Storage Repository (LIB-AV): 
- copy files to a staging directory
- get mediainfo metadata from files
- move files to the top level of the directory
- renames files and staging directory according to the LIB-AV naming convention
- prepares and arranges an ingest csv

`copy_and_rename.py` copies files to a new directory and adds a suffix to filenames using a csv to match
- files not listed in the csv or with no suffix given in the csv are skipped
- by default, files are skipped if a file with the new name already exists in the destination directory
  - use `-o` overwrite mode to change this
- script creates a log in the destination directory of files copied and files skipped

Bits and pieces adapted from [IFIscripts](https://github.com/Irish-Film-Institute/IFIscripts).
