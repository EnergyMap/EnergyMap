import numpy as np
import geopandas
from shapely.geometry import Polygon

def create_2d_array(minx, miny, maxx, maxy):    
    #creating a 2d array for all square tiles to cover the whole country (adding one for surity)
    rows = int(np.floor((maxy - miny) / 1000))
    cols = int(np.floor((maxx - minx) / 1000))
    two_d_arr = np.zeros((rows+1,cols+1))
    return two_d_arr

def create_geodataframe_with_squares(two_d_arr, column_name, minx, miny):
    squares = []
    sums = []
    for y in range(0, two_d_arr.shape[0]):
        for x in range(0, two_d_arr.shape[1]):
            co2 = two_d_arr[y,x]
            if co2 > 0:
                thisx = minx + x*1000
                thisy = miny + y*1000
                lat_point_list = [thisx, thisx+1000, thisx+1000, thisx, thisx]
                lon_point_list = [thisy, thisy, thisy+1000, thisy+1000, thisy]
                squares.append(Polygon(zip(lat_point_list, lon_point_list)))
                sums.append(co2)
    sqdf = geopandas.GeoDataFrame(crs="EPSG:3857", geometry=squares)
    sqdf[column_name] = sums
    return sqdf.to_crs("EPSG:4326")
    

def create_square_tiles(geodf):
    meter_geodf = geodf.to_crs("EPSG:3857")
    minx, miny, maxx, maxy = meter_geodf.total_bounds
    co2sums = create_2d_array(minx, miny, maxx, maxy)
    co2opts = create_2d_array(minx, miny, maxx, maxy)
    meter_geodf['centroid'] = meter_geodf.geometry.centroid
    #for some reason some centroids are none
    meter_geodf = meter_geodf.dropna(subset=['centroid'])
    #summing up co2 for every row in the dataframe to the correct square tile in the grid
    for index, row in meter_geodf.iterrows():
        co2sums[int(np.floor((row.centroid.y-miny)/1000))][int(np.floor((row.centroid.x-minx)/1000))] += row['co2/a']
        co2opts[int(np.floor((row.centroid.y-miny)/1000))][int(np.floor((row.centroid.x-minx)/1000))] += row['opt_co2']
        
    sqdf_co2 = create_geodataframe_with_squares(co2sums, 'co2/a', minx, miny)
    sqdf_opts = create_geodataframe_with_squares(co2opts, 'opt_co2', minx, miny)
    return (sqdf_co2, sqdf_opts)


def main():
    df = geopandas.read_file('../helsingor')
    sqrs, sqrs2 = create_square_tiles(df)
    sqrs.to_file('../helsingor_squares_co2')
    sqrs2.to_file('../helsingor_squares_opt')

if __name__ == "__main__":
    main()