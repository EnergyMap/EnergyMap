# EnergyMap

Mapping co2-emissions of buildings all over the world. The notebook "pipelinefinal" in the root folder displays the pipeline for one file from OpenStreetMap. The file pipeline/load.py contains the logic for downloading and processing (filtering out buildings, splitting to suitable size files) an updated extract of all European countries from Geofabrik. You will need Docker on the path to use load.py, otherwise you need to download manually. You will need an .env-file that contains the url-information for you database, see the last cells of "pipelinefinal" for more details.
