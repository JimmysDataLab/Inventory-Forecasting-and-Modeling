
import os
import pyarrow as pa
from datetime import datetime
import re
from dotenv import load_dotenv
from numpy import nan

load_dotenv()

_data_dir = os.getenv("DATA_DIR")

_names = [
        "test",
        "train",
        "transactions",
        "oil",
        "holidays_events",
       # "sample_submission",
        "stores",
        ]

_flat_schema = {
        "test":pa.schema([
            pa.field("id",pa.string()),
            pa.field("date",pa.string()),
            pa.field("store_nbr",pa.string()),
            pa.field("family",pa.string()),
            pa.field("onpromotion",pa.string())
    ]),
        "train":pa.schema([
            pa.field("id",pa.string()),
            pa.field("date",pa.string()),
            pa.field("store_nbr",pa.string()),
            pa.field("family",pa.string()),
            pa.field("sales",pa.string()),
            pa.field("onpromotion",pa.string())
    ]),
        "transactions":pa.schema([
            pa.field("date",pa.string()),
            pa.field("store_nbr",pa.string()),
            pa.field("transactions",pa.string())
    ]),
        "oil":pa.schema([
            pa.field("date",pa.string()),
            pa.field("dcoilwtico",pa.string()),
    ]),
        "holidays_events":pa.schema([
            pa.field("date",pa.string()),
            pa.field("type",pa.string()),
            pa.field("locale",pa.string()),
            pa.field("locale_name",pa.string()),
            pa.field("description",pa.string()),
            pa.field("transferred",pa.string())
    ]),
        "stores":pa.schema([
            pa.field("store_nbr",pa.string()),
            pa.field("city",pa.string()),
            pa.field("state",pa.string()),
            pa.field("type",pa.string()),
            pa.field("cluster",pa.string()),
    ]),
}

_schema = {
        "test":pa.schema([
            pa.field("id",pa.uint64()),
            pa.field("date",pa.date32()),
            pa.field("store_nbr",pa.uint64()),
            pa.field("family",pa.string()),
            pa.field("onpromotion",pa.uint64())
    ]),
        "train":pa.schema([
            pa.field("id",pa.uint64()),
            pa.field("date",pa.date32()),
            pa.field("store_nbr",pa.uint64()),
            pa.field("family",pa.string()),
            pa.field("sales",pa.float64()),
            pa.field("onpromotion",pa.uint64())
    ]),
        "transactions":pa.schema([
            pa.field("date",pa.date32()),
            pa.field("store_nbr",pa.uint64()),
            pa.field("transactions",pa.uint64())
    ]),
        "oil":pa.schema([
            pa.field("date",pa.date32()),
            pa.field("dcoilwtico",pa.float64()),
    ]),
        "holidays_events":pa.schema([
            pa.field("date",pa.date32()),
            pa.field("type",pa.string()),
            pa.field("locale",pa.string()),
            pa.field("locale_name",pa.string()),
            pa.field("description",pa.string()),
            pa.field("transferred",pa.string())
    ]),
        "stores":pa.schema([
            pa.field("store_nbr",pa.uint64()),
            pa.field("city",pa.string()),
            pa.field("state",pa.string()),
            pa.field("type",pa.string()),
            pa.field("cluster",pa.uint64()),
    ]),
}



def _check_int(x):
    try:
        int(x)
        return x
    except Exception as e:
        #print(e)
        return None

def _check_float(x):
    try:
        float(x)
        return x
    except Exception as e:
        #print(e)
        return None

def _check_date(x):
    try:
        datetime.strptime(re.sub(r"[-/.]", "-",x),"%Y-%m-%d")
        return x
    except Exception as e:
        #print(e)
        return None