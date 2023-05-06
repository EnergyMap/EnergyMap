import random, gc
import geopandas
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

def estimate_levels_with_randomforest(geodf):
    print('Predicting levels, please wait...')
    geodf['predicted'] = 0
    crs = geodf.crs
    geodf["geometry"] = geodf["geometry"].to_crs("EPSG:3857")
    geodf.loc[geodf['building:levels'].isna(),'predicted'] = 1
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
    train_size = min(max(30000,round(len(x)/20)), len(x)-10)
    #if there's not enough for training, then just return average level:
    if train_size < 100:
        geodf['levels'] = geodf['building:levels']
        geodf.loc[geodf['predicted']==1,'levels'] = int(geodf.loc[geodf['predicted']==0,'building:levels'].mean())
        print("Data size too small, using average level...")
    else:
        print('Using training data length ' + str(train_size))
        X_train, _, y_train, _ = train_test_split(
            x, y, train_size=train_size, random_state=42, shuffle=True
        )
        rfr = RandomForestRegressor(n_estimators=30, n_jobs=-1)
        print('Fitting model to data, please wait...')
        pred = rfr.fit(X_train, y_train).predict(predict_data)
        geodf['levels'] = geodf['building:levels']
        geodf.loc[geodf['predicted']==1,'levels'] = np.rint(pred)
        del data, train_data, predict_data, X_train, y_train, pred
        gc.collect()
    geodf["geometry"].to_crs(crs)
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
    geodf['levels'] = data[:,3]
    geodf['predicted'] = data[:,4]
    geodf["geometry"].to_crs(crs)
    return geodf



