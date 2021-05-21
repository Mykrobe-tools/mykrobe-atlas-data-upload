import argparse
from bsddb3 import db

DB_KEY_PREFIX_NEIGHBOURS = "n"
DB_KEY_PREFIX_DISTANCES = "d"
DB_INSERT_BATCH_SIZE = 1000


def _convert_key_to_bytes(key):
    return key.encode("utf-8")


def _store_clustered_neighbours_distance_in_berkeley_db(included_samples_file, sample_mapping_csv,
                                                        neighbours_distance_file, berkeley_db_file):
    included_samples = []
    with open(included_samples_file, 'r') as f:
        for line in f:
            included_samples.append(line.strip())

    isolate_to_tracking = {}
    with open(sample_mapping_csv, "r") as f:
        for line in f:
            isolate, experiment, tracking = line.strip().split(',', maxsplit=2)
            isolate_to_tracking[isolate.strip()] = tracking.strip()

    with open(neighbours_distance_file, "r") as f:
        storage = db.DB()
        storage.open(berkeley_db_file, None, db.DB_HASH, db.DB_CREATE)
        processed = 0
        total = 0
        for line in f:
            isolate, neighbours, distances = line.strip().split('\t', maxsplit=2)
            if isolate not in included_samples:
                continue
            if isolate not in isolate_to_tracking:
                continue
            source_sample = isolate_to_tracking[isolate]
            clustered_samples = [isolate_to_tracking[n] for n in neighbours.split(',')]
            storage[_convert_key_to_bytes(DB_KEY_PREFIX_NEIGHBOURS+source_sample)] = ','.join(clustered_samples).encode("utf-8")
            storage[_convert_key_to_bytes(DB_KEY_PREFIX_DISTANCES+source_sample)] = distances.encode("utf-8")
            processed = processed + 1
            if processed == DB_INSERT_BATCH_SIZE:
                storage.sync()
                total = total + processed
                print(f'Completed {total}')
                processed = 0
        if processed != 0:
            storage.sync()
            total = total + processed
            print(f'Completed {total}')
            processed = 0
        storage.close()
    print('Completed all!')


parser = argparse.ArgumentParser(description='Store clustered neighbours distance in cache database')
parser.add_argument('included_samples_file', type=str, help='Path to the included samples file')
parser.add_argument('sample_mapping_csv', type=str, help='Path to the sample mapping csv')
parser.add_argument('neighbours_distance_file', type=str, help='Path to the clustered neighbours distance file')
parser.add_argument('berkeley_db_file', type=str, help='Path to the berkeley db file')

if __name__ == '__main__':
    args = parser.parse_args()
    _store_clustered_neighbours_distance_in_berkeley_db(args.included_samples_file, args.sample_mapping_csv,
                                                        args.neighbours_distance_file, args.berkeley_db_file)