#!/usr/bin/env python3
import os
import argparse
import shutil
import re as _re
import json as _json
from pathlib import Path

JSON_EXTENSION = '.json'

def find_json_for_file(file):
    try:
        if file.with_name(file.name + JSON_EXTENSION).is_file():
            # file.jpg -> file.jpg.json
            the_json_path = file.with_name(file.name + JSON_EXTENSION)
        elif file.with_name(file.name.replace(file.suffix, JSON_EXTENSION)).is_file():
            # file.jpg -> file.json
            the_json_path = file.with_name(file.name.replace(file.suffix.lower(), JSON_EXTENSION))
        elif len(file.name) >= 47:
            # fileee...eee.jpg -> fileee...eee..json
            the_json_path = file.with_name(file.name[0:46] + JSON_EXTENSION)
        elif bool(_re.search(r'^(.+)(\(\d+\))(\..+)$', file.name)):
            weird_search = _re.search(r'^(.+)(\(\d+\))(\..+)$', file.name)
            if file.with_name(weird_search.group(1) + JSON_EXTENSION).is_file():
                # file(1).jpg -> file.json
                the_json_path = file.with_name(weird_search.group(1) + JSON_EXTENSION)
            else:
                # file(1).jpg -> file.jpg(1).json
                the_json_path = file.with_name(weird_search.group(1) + weird_search.group(3) + weird_search.group(2) + JSON_EXTENSION)
        with open(the_json_path, 'r') as f:
            json_dict = _json.load(f)
        print('Using ' + the_json_path.name + ' for ' + file.name)
        return the_json_path.name
    except:
        print(f'Couldn\'t find json for file: {file}')
        return None

parser = argparse.ArgumentParser()
parser.add_argument("folder", help="the folder that should be processed")
args = parser.parse_args()

file_counter = 0

print("\nMerging .json & .jpg files...")
for subdir, dirs, files in os.walk(args.folder):
    for filename in files:
        filepath = subdir + os.sep + filename
        filepath_lower = filepath.lower()
        if filepath_lower.endswith(".jpg") or filepath_lower.endswith(".heic") or filepath_lower.endswith(".png") or filepath_lower.endswith(".jpeg"):
            extension = Path(filepath).suffix
            # print(filepath)
            json_path = find_json_for_file(Path(filepath))
            if json_path != None:
                print(filepath)
                # print(json_path)
                merge_cmd = "exiftool -d %s -tagsfromfile \"" + subdir + os.sep +json_path + "\" " \
                "\"-GPSAltitude<GeoDataAltitude\" \"-GPSLatitude<GeoDataLatitude\" " \
                "\"-GPSLatitudeRef<GeoDataLatitude\" \"-GPSLongitude<GeoDataLongitude\" " \
                "\"-GPSLongitudeRef<GeoDataLongitude\" \"-Keywords<Tags\" " \
                "\"-Subject<Tags\" \"-Caption-Abstract<Description\" " \
                "\"-ImageDescription<Description\" \"-DateTimeOriginal<PhotoTakenTimeTimestamp\" " \
                "\"-CreateDate<CreationTimeTimestamp\" \"-ModifyDate<PhotoLastModifiedTimeTimestamp\" " \
                "-ext " + extension + " -overwrite_original "

                # print(merge_cmd + "\""+ filepath + "\"")
                retVal = os.system(merge_cmd + "\""+ filepath + "\"")
                file_counter += 1
                print()

print("Number of updated files: " + str(file_counter))

