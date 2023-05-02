# EnergyMap

Mapping co2-emissions of buildings all over the world. The notebook "pipelinefinal" in the root folder displays the pipeline for one file from OpenStreetMap.  
The file pipeline/load.py contains the logic for downloading and processing (filtering out buildings, splitting to suitable size files) an updated extract of all European countries from Geofabrik. You will need Docker on the path to use load.py, otherwise you need to download manually.  
You will need an .env-file that contains the url-information for your database, see the last cells of "pipelinefinal" for more details.

## Note on Geopandas issue

Please check your Geopandas version, it might have an issue in the method to insert data to postgis. You can find the relevant file at /usr/local/lib/python3.10/dist-packages/geopandas/io/sql.py , please check that the "text" method is being imported from sqlalchemy and that at around line 400 the code "SELECT Find SRID( etc" is wrapped in the text() method.  

This should be updated in the most recent Geopandas version.