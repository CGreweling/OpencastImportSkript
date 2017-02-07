# OpencastImportSkript

## How to use it
Edit config.py 

Run:
python select Series.py
 - Select the Series to import from the Source Server
 - Create a File(SelectedSeries) with the Selected Series or start to Ingest the Series
 
 The Episodes will be downloaded from the Source Server to local Diskstorage.
 Then the Episode will be uploaded from Local Storage to the Target Server via the Ingest Rest endpoint.

A TextFile with All Series of the Source Server will be created. 
The shema ist "SeriesName ; SeriesId" for simple Import into Excel sheet.
