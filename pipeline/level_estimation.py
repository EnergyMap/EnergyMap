import geopandas
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import random
from sklearn.ensemble import RandomForestRegressor

def predict_levels_with_randomforest(geodf):
    geodf['predict'] = 0
    crs = geodf.crs
    geodf["geometry"] = geodf["geometry"].to_crs("EPSG:3857")
    geodf.loc[geodf['building:levels'].isna(),'predict'] = 1
    areas = geodf["geometry"].area
    locations = geodf["geometry"].centroid
    levels = geodf["building:levels"]
    data = np.array([areas, locations.x, locations.y, levels]).T
    train_data = data[np.where(~np.isnan(data[:,3]))]
    predict_data = data[np.where(np.isnan(data[:,3]))][:, :3]
    #print(len(predict_data))
    #print(geodf.loc[geodf['predict']==1,'building:levels'].shape)
    x = train_data[:, :3]
    y = train_data[:, 3]
    rfr = RandomForestRegressor(criterion='absolute_error')
    pred = rfr.fit(x, y).predict(predict_data)
    geodf.loc[geodf['predict']==1,'building:levels'] = np.rint(pred)
    geodf["geometry"] = geodf["geometry"].to_crs(crs)
    return geodf

def predict_levels(with_levels_info, without_levels_info, k_neighbours):
    distances = cdist(without_levels_info[:,[0,1,2]], with_levels_info[:,[0,1,2]])
    idx = np.argpartition(distances, k_neighbours, axis=1)
    closest_k = idx[:,:k_neighbours]
    means = []
    for c in range(closest_k.shape[0]):
        means.append(int(np.mean(with_levels_info[closest_k[c,:], 3])))
    return means

def estimate_levels_with_knn(geodf, k_neighbours=3):
    print(f'Estimating levels for country {geodf.loc[geodf.index[0], "country"]}, this will take a while...')
    crs = geodf.crs
    geodf["geometry"] = geodf["geometry"].to_crs("EPSG:3857") # to meters instead of lat, lon degees
    
    areas = geodf["geometry"].area
    locations = geodf["geometry"].centroid
    levels = geodf["building:levels"]
    data = np.array([areas, locations.x, locations.y, levels]).T
    predicted = np.isnan(data[:,3]).reshape(-1,1)
    data = np.concatenate([data, predicted], axis=1)
    
    with_levels_info = data[np.where(~np.isnan(data[:,3]))]
    
    step = 10000
    L = []

    for i in range(0, data.shape[0], step):
        current = data[i:i+step,:]
        current_without_levels_info = np.where(np.isnan(current[:,3]))[0]
        means = predict_levels(with_levels_info, current[current_without_levels_info,:], k_neighbours)
        current[current_without_levels_info, 3] = means
        L.append(current)
        
    data = np.concatenate(L)
    
    #df = pd.DataFrame({"base_area": data[:,0], "x": data[:,1], "y": data[:,2],
    #                   "levels": data[:,3], "predicted": data[:,4]})
    geodf['levels'] = data[:,3]
    geodf['predicted'] = data[:,4]
    geodf["geometry"].to_crs(crs)
    return geodf



