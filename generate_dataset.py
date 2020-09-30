import argparse
from typing import List
import zipfile
import os
import shutil
import tqdm
import pandas as pd
import random

def get_file_id(geohash, date):
    year, month, day = date.split('-')
    datestr = f'{year}{month}{day}T000000'
    return f'{geohash}_{datestr}'

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--features_csv', type=str)
    parser.add_argument('--data_location', type=str)
    parser.add_argument('--output_location', type=str)
    parser.add_argument('--negative_sample', default=1.0, type=str)

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

pos_path = os.path.join(args.output_location, "hoppers")
neg_path = os.path.join(args.output_location, "no_hoppers")

# make directories for positive and negative labels
os.makedirs(pos_path, exist_ok=True)
os.makedirs(neg_path, exist_ok=True)

# loop over file and move to the correct directories
print('Moving files to label directories')
entries = os.listdir(args.data_location)
neg_files = {}
for entry in tqdm.tqdm(entries):
    if os.path.isfile(os.path.join(args.data_location, entry)):
        geohash, date, _ = entry.split('_')
        tile_id = f'{geohash}_{date}'
        if tile_id in pos_feature_ids:
            # copy to pos directory right away
            shutil.copy(os.path.join(args.data_location, entry), pos_path)
        else:
            # store the negative examples and process them after the fact since
            # we want randomize and shuffle
            if tile_id not in neg_files:
                neg_files[tile_id] = []
            neg_files[tile_id].append(os.path.join(args.data_location, entry))

# copy over a random sample of negative files
neg_files_list = list(neg_files.items())
random.shuffle(neg_files_list)
num_neg_files = int(len(neg_files_list) * float(args.negative_sample))
for idx in tqdm.trange(num_neg_files):
    for path in neg_files_list[idx][1]:
        shutil.copy(path, neg_path)

