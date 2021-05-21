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
    print(tree)


def _extract_minimum_spanning_tree(samples, mst):
    num_samples = len(samples)
    matrix = mst.toarray()

    # first iteration looks at the 0-distance samples and group them
    grouped_sets = []
    for row in range(num_samples - 1):
        for col in range(row + 1, num_samples):
            if matrix[row][col] == 1:
                new_set = True
                for s in grouped_sets:
                    if samples[row] in s:
                        s.add(samples[col])
                        new_set = False
                        break
                    elif samples[col] in s:
                        s.add(samples[row])
                        new_set = False
                        break
                if new_set:
                    grouped_sets.append({samples[row], samples[col]})
                matrix[row][col] = 0

    # second iteration connects those grouped sets and other singletons
    nodes = []
    relationships = []
    sample_to_node_id = {}
    for index, grouped_samples in enumerate(grouped_sets):
        nodes.append({
            "id": index,
            "samples": grouped_samples
        })
        for sample in grouped_samples:
            sample_to_node_id[sample] = index
    node_count = len(nodes)
    for row in range(num_samples - 1):
        for col in range(row + 1, num_samples):
            if matrix[row][col] > 1:
                start_index = 0
                if samples[row] in sample_to_node_id:
                    start_index = sample_to_node_id[samples[row]]
                else:
                    start_index = node_count
                    node_count = node_count + 1
                    sample_to_node_id[samples[row]] = start_index
                    nodes.append({
                        "id": start_index,
                        "samples": [samples[row]]
                    })

                end_index = 0
                if samples[col] in sample_to_node_id:
                    end_index = sample_to_node_id[samples[col]]
                else:
                    end_index = node_count
                    node_count = node_count + 1
                    sample_to_node_id[samples[col]] = end_index
                    nodes.append({
                        "id": end_index,
                        "samples": [samples[col]]
                    })

                relationships.append({
                    "start": start_index,
                    "end": end_index,
                    "distance": int(matrix[row][col] - 1)
                })
    return {
        "nodes": nodes,
        "distance": relationships
    }


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