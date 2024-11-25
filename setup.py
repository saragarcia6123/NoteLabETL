from kaggle.api.kaggle_api_extended import KaggleApi
import os
import csv
import json
import requests

FLAG_FILE = 'datasets_loaded.flag'

def download_datasets():

    api = KaggleApi()
    api.authenticate()

    datasets = ["ludmin/billboard"]

    for d in datasets:
        api.dataset_download_files(d, path=kaggle_datasets_path, unzip=True)

    print(f"Dataset downloaded and extracted to {kaggle_datasets_path}")

    files_to_keep = {"hot100.csv"}

    for file_name in os.listdir(kaggle_datasets_path):
        file_path = os.path.join(kaggle_datasets_path, file_name)

        if os.path.isfile(file_path) and file_name not in files_to_keep:
            os.remove(file_path)
            print(f"Removed {file_path}")
        else:
            print(f"Kept {file_path}")


    with open(FLAG_FILE, 'w') as f:
        f.write("TRUE")

    def main():
        if not os.path.exists(FLAG_FILE):
            download_datasets()
        else:
            print("Datasets already loaded, skipping...")


    if __name__ == "__main__":
        main()
