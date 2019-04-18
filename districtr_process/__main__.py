import json
import logging
import pathlib
from tqdm import tqdm

from glob import glob

import yaml

from .place import PlaceSchema
from .process import process

logging.captureWarnings(True)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def load(place_filename):
    schema = PlaceSchema()
    place_file = pathlib.Path(place_filename)
    if place_file.suffix == ".yaml" or place_file.suffix == ".yml":
        with open(place_file) as f:
            place = schema.load(yaml.load(f, Loader=yaml.SafeLoader))
    elif place_file.suffix == ".json":
        with open(place_file) as f:
            place = schema.load(json.load(f))
    else:
        raise TypeError("The given place filename is not in yaml or json format")
    return place


def fill_in_nones(pairs):
    for pair in pairs:
        if isinstance(pair, tuple) and len(pair) == 2:
            yield pair
        else:
            yield (pair, None)


def many(filenames, output_file, upload=True):
    records = [
        main(place_filename=place_filename, upload=upload)
        for place_filename in tqdm(filenames)
    ]
    print(records)
    with open(output_file, "w") as f:
        json.dump(records, f)


def main(place_filename, upload=True):
    print(place_filename)
    place = load(place_filename)

    units_records = [
        process(units, place["id"], upload=upload) for units in place["units"]
    ]
    place_record = place.copy()
    place_record["units"] = units_records

    return place_record


if __name__ == "__main__":
    filenames = list(glob("./data/*.yml"))
    main("./data/mississippi.yml", upload=True)
    many(filenames, "./output.json", upload=False)
