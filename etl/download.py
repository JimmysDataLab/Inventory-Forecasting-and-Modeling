import subprocess
import sys
import os
import etl.utils as utils
import shutil

print("download time bitch")


def _download_csv_data():

    os.makedirs(utils._data_dir,exist_ok=True)

    SH_SCRIPT = f"kaggle competitions download -c \
        store-sales-time-series-forecasting -p {utils._data_dir}/csv &&\
            unzip {utils._data_dir}/csv/store-sales-time-series-forecasting.zip\
                -d {utils._data_dir}/csv && \
                    rm {utils._data_dir}/csv/store-sales-time-series-forecasting.zip"


    shutil.rmtree(os.path.join(utils._data_dir,"csv"),ignore_errors=True)
    subprocess.run(SH_SCRIPT,shell=True,check=True)


if __name__ == "__main__":
    _download_csv_data()