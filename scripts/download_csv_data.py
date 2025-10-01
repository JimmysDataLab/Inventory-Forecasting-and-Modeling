'''
Check all required files in /data/raw
Download all if all not present
'''
import os
import subprocess
import sys
from dotenv import load_dotenv


load_dotenv()
data_dir = os.path.join(os.environ.get("DATA_DIR"),"raw")
os.makedirs(data_dir,exist_ok=True)

SH_SCRIPT = "kaggle competitions download -c \
    store-sales-time-series-forecasting -p $SSTSF_DATA_DIR/raw &&\
        unzip $SSTSF_DATA_DIR/raw/store-sales-time-series-forecasting.zip\
              -d $SSTSF_DATA_DIR/raw && \
                rm $SSTSF_DATA_DIR/raw/store-sales-time-series-forecasting.zip"

files = ["test.csv",
        "train.csv",
        "transactions.csv",
        "oil.csv",
        "holidays_events.csv",
        "sample_submission.csv",
        "stores.csv",
]

def main():
    '''
    Download files from Kaggle
    '''
    if set(os.listdir(data_dir)) == set(files):
        print("All files presesnt. Download data again? Input 'y/Y' for yes")
        ans = input()
        if ans.lower() == 'y' :
            print("Deleting data dir and downloading again")
            subprocess.run(SH_SCRIPT,shell=True,check=True)
        else:
            sys.exit()

    else:
        print("Files missing. Starting a full download")
        subprocess.run(SH_SCRIPT,shell=True,check=True)
        sys.exit()

if __name__=="__main__":
    main()
