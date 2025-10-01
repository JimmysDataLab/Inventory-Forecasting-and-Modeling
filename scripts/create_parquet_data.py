'''
Reads csv files from /data/raw with a schema and writes it as
parquet files to /data/parquet
'''
import os
import json
import shutil
from dotenv import load_dotenv
import pandas as pd

CHUNKSIZE = 10000

load_dotenv()
data_dir = os.getenv("DATA_DIR")

tables = ["test",
        "train",
        "transactions",
        "oil",
        "holidays_events",
        "sample_submission",
        "stores",
]

def main():
    '''
    Execute when calling create_parquet_data.py
    '''
    shutil.rmtree(os.path.join(data_dir,"parquet"))
    print("Removed existing folder")

    with open(os.path.join(data_dir,"schema","csv_read_schema.json"), 'r',encoding="UTF-8") as file:
        csv_read_schema = json.load(file)

    with open(os.path.join(data_dir,"schema","csv_date_schema.json"), 'r',encoding="UTF-8") as file:
        csv_date_schema = json.load(file)


    for file in files:
        path = os.path.join(data_dir,"raw",file)
        if path in csv_date_schema.keys():
            data = pd.read_csv(path,\
                        dtype=csv_read_schema.get(path),\
                            parse_dates=csv_date_schema.get(path),\
                                chunksize=CHUNKSIZE)
            for chunk in data:
                for unique_date in chunk.date.unique():
                    date_chunk = chunk[chunk.date == unique_date]
                    parquet_path = os.path.join(data_dir,"parquet",file.split('.',maxsplit=1)[0],\
                                        f"{unique_date.year}",f"{unique_date.month}")
                    print("writing",os.path.join(parquet_path,f"{unique_date.day}.parquet"))
                    os.makedirs(parquet_path,exist_ok=True)
                    date_chunk.to_parquet(os.path.join(parquet_path,f"{unique_date.day}.parquet"),\
                                          engine="pyarrow",index=False)
        else:
            data = pd.read_csv(path,\
                dtype=csv_read_schema.get(path),\
                    parse_dates=csv_date_schema.get(path),\
                        chunksize=CHUNKSIZE)
            parquet_path = os.path.join(data_dir,"parquet",file.split('.',maxsplit=1)[0])
            os.makedirs(parquet_path,exist_ok=True)
            for idx,chunk in enumerate(data):
                chunk.to_parquet(os.path.join(parquet_path,f"{str(idx)}.parquet"),\
                                                engine="pyarrow",\
                                                index=False)

def write_csv_to_parquet():
    '''
    Read csv and save to parquet
    '''
    pass


if __name__=="__main__":
    main()
