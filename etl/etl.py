from utils import _data_dir,_flat_schema,_schema,_check_date,_check_float,_check_int
import os
import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.ipc as ipc
import pyarrow.parquet as pq
from pandas import ArrowDtype
import shutil


def _extract(source:str,name:str):
    if source == 'csv':
        path = os.path.join(_data_dir,source,f"{name}.{source}")
        min_size = 1_000_000

        if os.path.getsize(path) > min_size *10:
            block_size = int(os.path.getsize(path)/os.cpu_count())
        else:
            block_size = None

        column_types = _flat_schema[name]
        batches = pa.csv.open_csv(path\
                                  ,read_options=csv.ReadOptions(use_threads=True,block_size=block_size)\
                                    ,convert_options=csv.ConvertOptions(check_utf8=True,column_types=column_types)
                                    )

    return batches


def _transform(obj,name:str):

    if isinstance(obj,pa._csv.CSVStreamingReader):
        for batch in obj:
            data = pa.Table.from_batches([batch]).to_pandas(types_mapper=ArrowDtype)
            for idy,field in enumerate(_schema[name].names):

                if _schema[name].types[idy] in [pa.uint64(),pa.uint32(),pa.uint16()]:
                    data[field] = data[field].apply(_check_int).astype("uint64[pyarrow]")

                elif _schema[name].types[idy] in [pa.float64(),pa.float32(),pa.float16()]:
                    data[field]=data[field].apply(_check_float).astype("float64[pyarrow]")

                elif _schema[name].types[idy] in [pa.date32(),pa.date64()]:
                    data[field]=data[field].apply(_check_date).astype("date32[pyarrow]")

                else:
                    pass

            yield data


def _load(obj,dest,name):

    if os.path.exists(os.path.join(_data_dir,dest,name)):
        shutil.rmtree(os.path.join(_data_dir,dest,name))
    os.makedirs(os.path.join(_data_dir,dest,name))
    try:
        if dest == "arrow":
            for idx,batch in enumerate(obj):
                with ipc.new_file(os.path.join(_data_dir,dest,name,f"{name}-{idx}.arrow")\
                                    ,schema=_schema[name]) as f:
                    f.write_table(pa.Table.from_pandas(batch, preserve_index=False))
            return True

        if dest == "parquet":
            for idx,batch in enumerate(obj):
                pq.write_table(pa.Table.from_pandas(batch,schema=_schema[name]),\
                               os.path.join(_data_dir,dest,name,f"{name}-{idx}.parquet"),\
                flavor="spark")
            return True

    except Exception as e:
        print(e)
        return False


def _etl(source,dest,name):

    batches = _extract(source,name)
    trans_batches = _transform(batches,name)
    status = _load(trans_batches,dest,name)

    return status

# if __name__ == "__main__":
#     _elt()
