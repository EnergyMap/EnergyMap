# EnergyMap

Mapping co2-emissions of buildings all over the world. This application requires a Linux environment with bash in order to function (because it relies on using subprocesses). The load_data-function requires Docker on the PATH.  

For downloading data (assuming you run python with the command 'python3'):

```
python3 load_data.py [folder where to save the data]
```
To run pipeline, i.e., process the data and import it to your postgis database:
```
python3 run_pipeline.py [the name of python in your command line, e.g., 'python3'] [folder where the data resides]
```
This python-file uses subprocesses, and therefore needs the name of python in your command line in order to run properly.  
  
If you want to follow how the pipeline advances on a more detailed level than the printed log, you can check the file "log.txt" that will be written to from the subprocesses.

## .env-file
In order to access your Postgis-database, you will need to add an .env-file with the following variables:

USER=[database user]  
PW=[password]  
DB=[name of database]  
PORT=[database port]  
URL=[database url]  
TABLE=[database table]

## Note on Geopandas issue

Please check your Geopandas version, it might have an issue in the method to insert data to postgis. You can find the relevant file at /usr/local/lib/python3.10/dist-packages/geopandas/io/sql.py , please check that the "text" method is being imported from sqlalchemy and that at around line 400 the code "SELECT Find SRID( etc" is wrapped in the text() method.  

This should be updated in the most recent Geopandas version.
