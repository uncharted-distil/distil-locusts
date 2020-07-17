import argparse
import os
import csv

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--download_location', type=str)
    parser.add_argument('--output_location', type=str)

    return parser.parse_args()

args = parse_args()

# read zip file and save geohash, time
entries = os.listdir(args.download_location)
with open(f'{args.output_location}/metadata.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['geohash', 'date', 'id'])
    for entry in entries:
        date, time = os.path.splitext(entry)[0].split('_')
        writer.writerow([date, time, entry])

