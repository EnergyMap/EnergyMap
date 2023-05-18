import geopandas
from log import log

#Calculates the energy demand for different climate zones in the data
#Parameter, dataframe: geodf
#Parameter, dataframe: zones
def get_energy_demand(geodf, zones):
    log(f'Estimating energy demand per climate zone for country {geodf.loc[geodf.index[0], "country"]}, this will take a while...')
    crs = geodf.crs
    geodf["geometry"] = geodf["geometry"].to_crs("EPSG:3857")
    geodf["floorarea"] = geodf.area * geodf["levels"]
    for i, index in enumerate(zones.index):
        part = geodf.geometry.centroid.to_crs(zones.crs).within(zones.loc[index,'geometry'])
        geodf.loc[part,'kWh/a'] = geodf.loc[part]['floorarea'] * zones.loc[index,'kWh/a']
    geodf["geometry"] = geodf["geometry"].to_crs(crs)
    return geodf

