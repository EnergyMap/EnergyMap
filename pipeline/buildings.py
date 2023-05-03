import osmium
import shapely.wkb as wkblib
import geopandas
import pandas as pd
import re

#An osmium-based class that reads the osm-file and appends all buildings to an array 
class BuildingHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.building_count = 0
        self.buildings = []
        # A global factory that creates WKB from a osmium geometry
        self.wkbfab = osmium.geom.WKBFactory()
        
    def area(self, w):
        if w.tags.get("building") == 'yes':
            try:
                wkb = self.wkbfab.create_multipolygon(w)
                geo = wkblib.loads(wkb, hex=True)
            except Exception as e:
                print(e)
                return
            row = { "w_id": w.id, "geometry": geo }

            for key, value in w.tags:
                row[key] = value

            self.buildings.append(row)
            self.building_count += 1
            
#function during workflow to test logic, default for test
def extract_country_name(file='filtered-bosnia-herzegovina-latest'):
    regex = '-[0-3]{2}'
    country = file.split('-latest')[0]
    if 'filtered-' in file:
        country = country.split('tered-')[1]
    if '/' in country:
        country = country.split('/')
        country = country[len(country)-1]
    if re.search(regex, country):
        country = re.split(regex, country)[0]
    return country
    

#Builds a geopandas-dataframe from an osm-file with the help of the osmium-based buildinghandler-class
#Parameter, string: osm-file location
def create_geodataframe(file):
    print(f'Loading osm-data from file {file}, this will take a while...')
    buildinghandler = BuildingHandler()
    buildinghandler.apply_file(file, locations=True)

    #This loop is needed beause of geopandas.GeoDataFrame otherwise using too much RAM at once
    #This loop should work with at least 16GB RAM
    print(f'Creating geodataframe from the data from {file}, this will take a while...')
    i = 200000
    while i-200000 < len(buildinghandler.buildings):
        dfx = pd.DataFrame(buildinghandler.buildings[(i-200000):min([i, len(buildinghandler.buildings)-1])])
        gdfx = geopandas.GeoDataFrame(dfx, geometry='geometry')
        gdfx = gdfx.set_crs("EPSG:4326")
        #gdfx = ox.project_gdf(gdfx)
        #gdfx = gdfx.dropna(subset=['building:levels'])
        gdfx = gdfx[['w_id', 'geometry', 'building:levels']]
        if i < 200001:
            geodf = gdfx
        else:
            geodf = pd.concat([geodf, gdfx])
        i += 200000
    geodf.loc[geodf['building:levels'].str.contains('[^0-9]', na=False)] = None
    #geodf.loc[geodf['building:levels'].str.contains('[A-Za-z]', na=False)] = None
    #geodf.loc[geodf['building:levels'].str.contains('[;,.-`й]', na=False)] = None
    geodf.loc[geodf['building:levels'] == "0"] = None
    geodf["building:levels"] = geodf["building:levels"].astype("float")
    
    #some rows will not have any shape, and should be deleted
    geodf = geodf[~geodf["geometry"].isna()]
    
    #finding the country from the filename and adding to the dataframe
    geodf['country'] = extract_country_name(file)
    geodf.reset_index(drop=True, inplace=True)
    return geodf

def main():
    #result = build_geodf('albania-latest.osm.pbf')
    #print(result.head())
    #print(result.shape)
    #split_big_countries()
    print(extract_country_name())

if __name__ == "__main__":
    main()
