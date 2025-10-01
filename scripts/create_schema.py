'''
Creates a json schema file from hard coded dictionary
'''
import os
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()
data_dir = os.getenv("DATA_DIR")

csv_read_schema = {"test" :{ \
        "id":"Int64",
        "date":"string",
        "store_nbr":"category",
        "family":"category",
        "onpromotion":"category"},

        "train.csv" : { \
            "id":"Int64",
            "date":	"string",
            "store_nbr":"category",
            "family":"category",
            "onpromotion":"category"},

        "transactions" : { \
            "date":"string",
            "store_nbr":"category",
            "transactions":"Int64"},

        "oil" : { \
            "date":"string",
            "dcoilwtico":"Float64"},

        "holidays_events" : { \
            "date":"string",
            "type":"category",
            "locale":"category",
            "locale_name":"category",
            "description":"category",
            "transferred":"boolean"},

        "stores" : { \
            "store_nbr":"category",
            "city":"category",
            "state":"category",
            "type":"category",
            "cluster":"category"},
}

csv_date_schema = {"test":["date"],
    "train":["date"],
    "transactions" :["date"],
    "oil" :["date"],
    "holidays_events" :["date"]
}

def main():

    if os.path.exists(os.path.join(data_dir,"schema")):
        print("Removing existing schema directory\n")
        shutil.rmtree(os.path.join(data_dir,"schema"))

    print("Creating new schema directory\n")
    os.makedirs(os.path.join(data_dir,"schema"),exist_ok=True)

    with open(os.path.join(data_dir,"schema","csv_read_schema.json"),"w",encoding="UTF-8") as file:
        file.write(json.dumps(csv_read_schema,indent=4))

    with open(os.path.join(data_dir,"schema","csv_date_schema.json"),"w",encoding="UTF-8") as file:
        file.write(json.dumps(csv_date_schema,indent=4))

    print("schemas created:\n")
    for schema in Path(os.path.join(data_dir,"schema")).rglob("*.json"):
        print(schema.relative_to(Path.home()),"\n")

if __name__=="__main__":
    main()

