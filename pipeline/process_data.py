import os, psutil, gc, sys
import pandas as pd
from dotenv import dotenv_values
from sqlalchemy import create_engine
from buildings import create_geodataframe
from level_estimation import estimate_levels_with_knn, estimate_levels_with_randomforest
from climate_zones import get_climate_zones
from energy_demand import get_energy_demand
from co2_emissions import get_co2_emissions
from square_tiles import create_square_tiles
from log import log

def create_emission_data(file):
    gdf = create_geodataframe(file)
    if len(gdf) == 0:
        return None
    gdf = estimate_levels_with_randomforest(gdf)
    zones = get_climate_zones()
    gdf = get_energy_demand(gdf, zones)
    co2_rates = pd.read_csv('pipeline/co2rates.csv', index_col=0)
    gdf = get_co2_emissions(gdf, co2_rates)
    sqdf_co2, sqdf_opts, sqdf_diff = create_square_tiles(gdf)
    return (gdf, sqdf_co2, sqdf_opts, sqdf_diff)

def list_files(folder):
    return [x for x in os.listdir(folder) if '.osm.pbf' in x and '-ready' not in x]

def create_connection():
    cf = dotenv_values(".env")
    db_url = f'postgresql://{cf["USER"]}:{cf["PW"]}@{cf["URL"]}:{cf["PORT"]}/{cf["DB"]}'
    connection = create_engine(db_url)  
    return connection

def process_file(file):
    emission_data = create_emission_data(file)
    if emission_data:
        gdf, sqdf_co2, sqdf_opts, sqdf_diff = emission_data
    else:
        log('No buildings in ' + file)
        return
    db_conn = create_connection()
    #insert_in_database(db_conn, 'buildings', gdf)
    #insert_in_database(db_conn, 'squares_co2', sqdf_co2)
    #insert_in_database(db_conn, 'squares_opt_co2', sqdf_opts)
    #insert_in_database(db_conn, 'squares_diff', sqdf_diff)
    log(f'Finished processing {file}.')
    #probably unnecessary, but since memory has been a problem in this pipeline:
    del emission_data, gdf, sqdf_co2, sqdf_opts, sqdf_diff
    gc.collect()
    
def run_pipeline(folder='OSM_data'):
    files = list_files(folder)
    for file in files:
        log(file)
        log('Using memory before handling file '+str(psutil.virtual_memory().percent))
        process_file(os.path.join(folder,file))
        os.rename(os.path.join(folder,file), os.path.join(folder,file+'-ready'))
        log('Using memory after handling file '+str(psutil.virtual_memory().percent))

def insert_in_database(connection, table, gdf):
    log(f'Inserting into db-table "{table}" for {gdf.loc[gdf.index[0], "country"]}, please wait...')
    gdf.to_postgis(table, connection, if_exists="append") 

def main():
    if len(sys.argv) > 2:
        print('Please use this script with only one argument: work-folder')
        return
    if len(sys.argv) > 1:
        folder = os.path.join(os.getcwd(),sys.argv[1])
    else:
        folder = os.getcwd()
    run_pipeline(folder)

if __name__ == "__main__":
    main()
