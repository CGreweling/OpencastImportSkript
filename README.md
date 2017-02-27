# OpencastImportSkript

## How to use it
Edit config.py 

Run:
python select Series.py
 - Select the Series to import from the Source Server
 - Create a File(SelectedSeries) with the Selected Series 
 - Or start to Ingest the Series:
 
 All Episodes of each selected Series will be downloaded from the Source Server to local Diskstorage.
 Then the Episode will be uploaded from Local Storage to the Target Server via the Ingest Rest endpoint.

A TextFile with All Series of the Source Server will be created in this Programmfolder. 
The shema ist "SeriesName ; SeriesId" for simple Import into Excel sheet.
So a non IT-Guy can sort and select the wanted Series.

## Importing from Commandline

To import Series from a file where a Series Id is in each line:
for line in $(cat SelectedSeries.txt); do python exportSeries.py $line; done
The Same for Importing Episodes from a File:
for line in $(cat SelectedEpisodes.txt); do python exportEpisode.py $line; done
