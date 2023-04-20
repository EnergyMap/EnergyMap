import numpy as np
import geopandas
from shapely.geometry import Polygon

def create_2d_array(geodf):
    minx, miny, maxx, maxy = geodf.total_bounds
    #creating a 2d array for all square tiles to cover the whole country (adding one for surity)
    rows = int(np.floor((maxy - miny) / 1000))
    cols = int(np.floor((maxx - minx) / 1000))
    co2sums = np.zeros((rows+1,cols+1))
    return co2sums

def create_geodataframe_with_squares(co2sums):
    squares = []
    sums = []
    for y in range(0, co2sums.shape[0]):
        for x in range(0, co2sums.shape[1]):
            co2 = co2sums[y,x]
            if co2 > 0:
                thisx = minx + x*1000
                thisy = miny + y*1000
                lon_point_list = [thisx, thisx+1000, thisx+1000, thisx, thisx]
                lat_point_list = [thisy, thisy, thisy+1000, thisy+1000, thisy]
                squares.append(Polygon(zip(lon_point_list, lat_point_list)))
                sums.append(co2)
    sqdf = geopandas.GeoDataFrame(crs=geodf.crs, geometry=squares)
    sqdf['co2'] = sums
    return sqdf
    

def create_square_tiles(geodf):
    co2sums = create_2d_array(geodf)
    geodf['centroid'] = geodf.geometry.centroid
    #for some reason some centroids are none
    geodf = geodf.dropna(subset=['centroid'])
    #summing up co2 for every row in the dataframe to the correct square tile in the grid
    for index, row in geodf.iterrows():
        co2sums[int(np.floor((row.centroid.y-miny)/1000))][int(np.floor((row.centroid.x-minx)/1000))] += row.co2
        
    sqdf = create_geodataframe_with_squares(co2sums)
    return sqdf
