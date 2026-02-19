import argparse
import logging
import os
import shutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

LOGGER = logging.getLogger(__name__)

DATASET_COMPETITIONS = {
    "store-sales": "store-sales-time-series-forecasting",
    "walmart": "walmart-recruiting-store-sales-forecasting",
}


def _resolve_data_dir() -> Path:
    data_dir = os.getenv("DATA_DIR") or "data"
    return Path(data_dir)


def _download_csv_data(dataset: str) -> Path:
    data_dir = _resolve_data_dir()
    dataset = dataset.strip().lower()
    competition = DATASET_COMPETITIONS.get(dataset)
    if not competition:
        raise ValueError(f"Unknown dataset: {dataset}")

    csv_dir = data_dir / "csv" / dataset
    csv_dir.mkdir(parents=True, exist_ok=True)

    zip_path = csv_dir / f"{competition}.zip"
    sh_script = (
        f"kaggle competitions download -c {competition} -p {csv_dir} && "
        f"unzip {zip_path} -d {csv_dir} && "
        f"rm {zip_path}"
    )

    LOGGER.info("Downloading %s to %s", competition, csv_dir)
    shutil.rmtree(csv_dir, ignore_errors=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(sh_script, shell=True, check=True)

    for nested_zip in csv_dir.glob("*.zip"):
        LOGGER.info("Extracting %s", nested_zip.name)
        subprocess.run(
            f"unzip -o {nested_zip} -d {csv_dir}",
            shell=True,
            check=True,
        )
    return csv_dir


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Kaggle competition data.")
    parser.add_argument(
        "--dataset",
        choices=sorted(DATASET_COMPETITIONS.keys()),
        default="store-sales",
        help="Dataset to download.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = _parse_args()
    _download_csv_data(args.dataset)