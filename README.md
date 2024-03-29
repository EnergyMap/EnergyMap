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
BUILDING_TABLE=[database table for building data]  
SQUARES_CO2_TABLE=[database table for 1 km square sums]  
SQUARES_CO2_OPT_TABLE=[database table for 1 km square sums optimal co2 emission]  
SQUARES_DIFF_TABLE=[database table for 1 km square sums difference between current and optimal]

## Dependencies

Although there is a requirements.txt-file, we highly recommend to use the file misc/install.sh as a list of which libraries will be needed. Using the .txt-file seems to cause unexplained errors with inconsistent dependencies.

## Note on system requirements

PyOsmium and Geopandas gather quite a lot of artefacts in memory, and therefore this pipeline has not been run successfully with less than 32GB of RAM memory. Also note, that the Random Forest Regression algorithm might demand quite a lot of execution time, and we strongly recommend executing the pipeline on a device with a multitude of cores.

## Note on Geopandas issue

Please check your Geopandas version, it might have an issue in the method to insert data to postgis. You can find the relevant file at /usr/local/lib/python3.10/dist-packages/geopandas/io/sql.py , please check that the "text" method is being imported from sqlalchemy and that at around line 400 the code "SELECT Find SRID( etc" is wrapped in the text() method.  

This should be updated in the most recent Geopandas version.
