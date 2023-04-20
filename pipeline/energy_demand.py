import geopandas

#Calculates the energy demand for different climate zones in the data
#Parameter, dataframe: geodf
#Parameter, dataframe: zones
def get_energy_demand(geodf, zones):
    crs = geodf.crs
    geodf["geometry"] = geodf["geometry"].to_crs("EPSG:3857")
    for i, index in enumerate(zones.index):
        part = geodf.geometry.centroid.to_crs(zones.crs).within(zones.loc[index,'geometry'])
        geodf.loc[part,'kWh/a'] = geodf.loc[part]['floorarea'] * zones.loc[index,'kWh/a']
    geodf["geometry"] = geodf["geometry"].to_crs(crs)
    return geodf

