import argparse
import zipfile
import os
import shutil
import tqdm
import pandas as pd

def get_file_id(geohash, date):
    year, month, day = date.split('-')
    datestr = f'{year}{month}{day}T000000'
    return f'{geohash}_{datestr}'

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--features_csv', type=str)
    parser.add_argument('--data_location', type=str)

    return parser.parse_args()

args = parse_args()

# load the tile / label info
features = pd.read_csv(args.features_csv)
positives = features['hoppers'] == 1
positive_features = features[positives]

pos_feature_ids = set()
for pos_row in positive_features.iterrows():
    id = get_file_id(pos_row[1]['geohash'], pos_row[1]['date'])
    pos_feature_ids.add(id)

pos_path = os.path.join(args.data_location, "hoppers")
neg_path = os.path.join(args.data_location, "no_hoppers")

# make directories for positive and negative labels
os.makedirs(pos_path, exist_ok=True)
os.makedirs(neg_path, exist_ok=True)

# loop over file and move to the correct directories
print('Moving files to label directories')
entries = os.listdir(args.data_location)
for entry in tqdm.tqdm(entries):
    if os.path.isfile(os.path.join(args.data_location, entry)):
        geohash, date, _ = entry.split('_')
        unique_id = f'{geohash}_{date}'
        if unique_id in pos_feature_ids:
            shutil.move(os.path.join(args.data_location, entry), pos_path)
        else:
            shutil.move(os.path.join(args.data_location, entry), neg_path)