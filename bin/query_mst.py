import argparse
import json
import ast
from bsddb3 import db
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree


DB_KEY_PREFIX_NEIGHBOURS = "n"
DB_KEY_PREFIX_DISTANCES = "d"


def _convert_key_to_bytes(key):
    return key.encode("utf-8")


def _query_for_mst(sample_id, berkeley_db_file):
    neighbours, distances = _query_db(berkeley_db_file, sample_id)
    samples = neighbours.split(',')
    num_samples = len(samples)
    input_matrix = csr_matrix(np.frombuffer(ast.literal_eval(distances), dtype=np.uint8).reshape(num_samples, num_samples))
    mst = minimum_spanning_tree(input_matrix)
    tree = _extract_minimum_spanning_tree(samples, mst)
    print(json.dumps(tree))


def _extract_minimum_spanning_tree(samples, mst):
    relationships = []
    num_samples = len(samples)
    matrix = mst.toarray()
    for row in range(num_samples - 1):
        for col in range(row + 1, num_samples):
            if matrix[row][col] > 0:
                relationships.append({
                    "start": samples[row],
                    "end": samples[col],
                    "distance": int(matrix[row][col] - 1)
                })
    return relationships


def _query_db(berkeley_db_file, sample_id):
    storage = db.DB()
    storage.open(berkeley_db_file, None, db.DB_HASH, db.DB_CREATE)
    neighbours = storage[_convert_key_to_bytes(DB_KEY_PREFIX_NEIGHBOURS + sample_id)].decode("utf-8")
    distances = storage[_convert_key_to_bytes(DB_KEY_PREFIX_DISTANCES + sample_id)].decode("utf-8")
    storage.close()
    return neighbours, distances


parser = argparse.ArgumentParser(description='Query the distance cache database and generate mst')
parser.add_argument('sample_id', type=str, help='Id of the sample we are looking for cluster')
parser.add_argument('berkeley_db_file', type=str, help='Path to the berkeley db file')


if __name__ == '__main__':
    args = parser.parse_args()
    _query_for_mst(args.sample_id, args.berkeley_db_file)