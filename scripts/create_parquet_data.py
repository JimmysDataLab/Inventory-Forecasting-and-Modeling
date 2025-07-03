'''
Reads csv files from /data/raw with a schema and writes it as
parquet files to /data/parquet
'''
import os
import json
import pandas as pd

data_dir = os.getenv("SSTSF_DATA_DIR")

files = ["test.csv",
        "train.csv",
        "transactions.csv",
        "oil.csv",
        "holidays_events.csv",
        "sample_submission.csv",
        "stores.csv",
]

os.makedirs(os.path.join(data_dir,"parquet"),exist_ok=True)

with open(os.path.join(data_dir,"schema","csv_read_schema.json"), 'r',encoding="UTF-8") as file:
    csv_read_schema = json.load(file)

with open(os.path.join(data_dir,"schema","csv_date_schema.json"), 'r',encoding="UTF-8") as file:
    csv_date_schema = json.load(file)


for file in files:
    path = os.path.join(data_dir,"raw",file)
    data = pd.read_csv(path,\
                       dtype=csv_read_schema.get(path),\
                        parse_dates=csv_date_schema.get(path))
    data.to_parquet(os.path.join(data_dir,\
                                 "parquet",file.split('.',maxsplit=1)[0]+".parquet"),\
                                    engine="pyarrow",\
                                        index=False)
    