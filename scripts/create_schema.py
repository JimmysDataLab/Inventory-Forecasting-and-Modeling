'''
Creates a json schema file from hard coded dictionary
'''
import os
import json

data_dir = os.getenv("SSTSF_DATA_DIR")

csv_read_schema = {os.path.join(data_dir,"raw","test.csv"):{ \
        "id":"category",
        "date":"string",
        "store_nbr":"category",
        "family":"category",
        "onpromotion":"category"},

        os.path.join(data_dir,"raw","train.csv"): { \
            "id":"category",
            "date":	"string",
            "store_nbr":"category",
            "family":"category",
            "onpromotion":"category"},

        os.path.join(data_dir,"raw","transactions.csv"): { \
            "date":"string",
            "store_nbr":"category",
            "transactions":"Int64"},

        os.path.join(data_dir,"raw","oil.csv"): { \
            "date":"string",
            "dcoilwtico":"Float64"},

        os.path.join(data_dir,"raw","holidays_events.csv"): { \
            "date":"string",
            "type":"category",	
            "locale":"category",
            "locale_name":"category",
            "description":"category",
            "transferred":"boolean"},

        os.path.join(data_dir,"raw","stores.csv"): { \
            "store_nbr":"category",
            "city":"category",
            "state":"category",
            "type":"category",
            "cluster":"category"},
}

csv_date_schema = {os.path.join(data_dir,"raw","test.csv"):["date"],
    os.path.join(data_dir,"raw","train.csv"):["date"],
    os.path.join(data_dir,"raw","transactions.csv"):["date"],
    os.path.join(data_dir,"raw","oil.csv"):["date"],
    os.path.join(data_dir,"raw","holidays_events.csv"):["date"]
}

os.makedirs(os.path.join(data_dir,"schema"),exist_ok=True)

with open(os.path.join(data_dir,"schema","csv_read_schema.json"),"w",encoding="UTF-8") as file:
    file.write(json.dumps(csv_read_schema,indent=4))

with open(os.path.join(data_dir,"schema","csv_date_schema.json"),"w",encoding="UTF-8") as file:
    file.write(json.dumps(csv_date_schema,indent=4))

print("schemas created\n")
print(os.listdir(os.path.join(data_dir,"schema")))
