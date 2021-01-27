import argparse

from bigsi.constants import DEFAULT_BERKELEY_DB_STORAGE_CONFIG, DEFAULT_ROCKS_DB_STORAGE_CONFIG, \
    DEFAULT_REDIS_STORAGE_CONFIG
from bigsi.graph.metadata import SampleMetadata
from bigsi.storage import get_storage


BERKELEYDB = "berkeleydb"
REDIS = "redis"
ROCKSDB = "rocksdb"


def _determine_config(storage_engine, storage_filename=None):
    if storage_filename:
        if storage_engine == REDIS:
            [host, port] = storage_filename.split(':')
            storage_config = {
                "host": host, "port": port
            }
        else:
            storage_config = {"filename": storage_filename}
    else:
        if storage_engine == BERKELEYDB:
            storage_config = DEFAULT_BERKELEY_DB_STORAGE_CONFIG
        elif storage_engine == ROCKSDB:
            storage_config = DEFAULT_ROCKS_DB_STORAGE_CONFIG
        else:
            storage_config = DEFAULT_REDIS_STORAGE_CONFIG

    config = {
        "storage-engine": storage_engine,
        "storage-config": storage_config
    }

    return config


def _migrate(id_mapping_filepath, db_storage_engine, storage_filepath=None):
    config = _determine_config(db_storage_engine, storage_filepath)
    storage = get_storage(config)
    current_metadata = SampleMetadata(storage)
    with open(id_mapping_filepath, 'r') as infile:
        for line in infile:
            isolate_id, _, tracking_id = line.strip().split(",")
            if tracking_id and tracking_id != isolate_id:
                colour = current_metadata.sample_to_colour(isolate_id)
                if colour:
                    current_metadata._validate_sample_name(tracking_id)
                    current_metadata._set_sample_colour(tracking_id, colour)
                    current_metadata._set_colour_sample(colour, tracking_id)
                    current_metadata._set_sample_colour(isolate_id, -1)

    storage.sync()
    storage.close()


parser = argparse.ArgumentParser(description='Migrate sample names from isolate IDs to Atlas tracking IDs.')
parser.add_argument('id_mapping_filepath', type=str, help='Path to the old-new ID mapping pickle file')
parser.add_argument('db_storage_engine', type=str, choices=[BERKELEYDB, ROCKSDB, REDIS], help='Storage engine')
parser.add_argument('--storage_filepath', type=str, default=None, help='berkeleydb/rocksdb filename or redis host:port')

if __name__ == '__main__':
    args = parser.parse_args()
    _migrate(args.id_mapping_filepath, args.db_storage_engine, args.storage_filepath)