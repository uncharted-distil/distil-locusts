import json
import warnings
from datetime import timedelta
import pandas as pd
import argparse
import os

warnings.filterwarnings('ignore')

import ee
ee.Initialize()

import geopandas as gpd
import geohash
from shapely import geometry
from polygon_geohasher.polygon_geohasher import polygon_to_geohashes

def get_locusthub_df(csv_path, geojson_path):
    '''
    clean up raw csv data from locusthub data and subset to only geojson region
    '''
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df.STARTDATE)

    country = json.load(open(geojson_path))['features'][0]
    polygon = ee.Geometry.Polygon(country['geometry']['coordinates'])
    polygon = geometry.shape(polygon.toGeoJSON())
    geohashes = polygon_to_geohashes(polygon, precision=5, inner=5)
    geohashes_country = sorted(list(geohashes))

    df['gh'] = df[['Y', 'X']].apply(lambda x: geohash.encode(*x, precision=5), axis=1).values
    df = df.loc[df.STARTDATE > '2016-01-01'].loc[df['gh'].isin(geohashes_country)]
    df = df[['gh', 'Y', 'X', 'date']]

    return df

def get_labels(df, df_label, label_name='hoppers', n_neighbor=0):
    '''
        add locust information to the features metadata
    '''
    df[label_name] = 0
    for row in df_label.iterrows():
        start_day = row[1].date
        end_day = start_day + timedelta(days=30)
        gh = set([row[1].gh])
        if n_neighbor > 0:
            for _ in range(n_neighbor):
                for g in list(gh):
                    gh |= set(geohash.expand(g))
        gh = list(gh)
        idx = df[label_name].loc[df['geohash'].isin(gh)].loc[df['date'] >= start_day].loc[
            df['date'] < end_day].index.values
        df[label_name].iloc[idx] = 1
    return df

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hoppers_csv_path', type=str, help='get from https://locust-hub-hqfao.hub.arcgis.com/datasets/hoppers-1')
    parser.add_argument('--geojson_path', type=str)
    parser.add_argument('--metadata_path', type=str)
    parser.add_argument('--save_path', type=str)

    return parser.parse_args()

args = parse_args()

print('getting features / labels / metadata')
# Read in hopper label data, feature metadata, and features
df_hoppers = get_locusthub_df(args.hoppers_csv_path, args.geojson_path)
df_meta = pd.read_csv(args.metadata_path)

# Add missing info
df_meta['date'] = pd.to_datetime(df_meta.date)
df_meta['lat'] = df_meta.apply(lambda rec: geohash.decode(rec['geohash'])[1], axis=1)
df_meta['lon'] = df_meta.apply(lambda rec: geohash.decode(rec['geohash'])[0], axis=1)
df_meta = df_meta[['path', 'date', 'geohash', 'lat', 'lon']]

# Create labels
df_label = get_labels(df_meta, df_hoppers, 'hoppers', n_neighbor = 0)

df_label.to_csv(os.path.join(args.save_path, 'features.csv'))