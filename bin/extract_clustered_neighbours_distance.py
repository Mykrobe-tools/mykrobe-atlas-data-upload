import argparse
import numpy as np


def _extract_nearest_neighbours_distance(included_samples_file, distance_matrix_file, distance_threshold):
    included_samples = []
    with open(included_samples_file, 'r') as f:
        for line in f:
            included_samples.append(line.strip())

    sample_index_map = {}
    for index, sample in enumerate(included_samples):
        sample_index_map[sample] = index

    # extract the whole distance matrix for the included samples only
    distance_matrix = _extract_distance_matrix(distance_matrix_file, distance_threshold, included_samples, sample_index_map)

    # now extract only clustered (nearest) neighbours for a given sample
    num_samples = len(included_samples)
    for index, source_sample in enumerate(included_samples):
        target_indices = [target_index for target_index in range(num_samples) if distance_matrix[index][target_index] > 0]
        num_neighbours = len(target_indices)
        sliced_distance_matrix = np.zeros((num_neighbours, num_neighbours), dtype=np.uint8)
        for row in range(num_neighbours-1):
            for col in range(row, num_neighbours):
                sliced_distance_matrix[row][col] = distance_matrix[target_indices[row]][target_indices[col]]
        target_samples = ','.join([included_samples[index] for index in target_indices])
        print(f"{source_sample}\t{target_samples}\t{sliced_distance_matrix.tostring()}")
    pass


def _extract_distance_matrix(distance_matrix_file, distance_threshold, included_samples, sample_index_map):
    num_samples = len(included_samples)
    distance_matrix = np.zeros((num_samples, num_samples), dtype=np.uint8)
    with open(distance_matrix_file, 'r') as f:
        first_line = next(f)
        target_list = list(map(lambda x: x.strip(), first_line.rstrip().split('\t')))
        for line in f:
            distances = line.rstrip().split('\t')
            source_sample = distances[0].strip()
            if source_sample not in sample_index_map:
                continue
            row_index = sample_index_map[source_sample]
            for i in range(1, len(distances)):
                target_sample = target_list[i]
                if target_sample not in sample_index_map:
                    continue
                if distance_threshold >= int(distances[i]):
                    col_index = sample_index_map[target_sample]
                    distance_matrix[row_index][col_index] = int(distances[i]) + 1
    return distance_matrix


parser = argparse.ArgumentParser(description="Extract distances of nearest neighbours")
parser.add_argument('included_samples_file', type=str, help='Path to the included samples file')
parser.add_argument('distance_matrix_file', type=str, help='Path to the distance matrix file')
parser.add_argument('distance_threshold', type=int, help='The distance threshold for nearest neighbours')

if __name__ == '__main__':
    args = parser.parse_args()
    _extract_nearest_neighbours_distance(args.included_samples_file, args.distance_matrix_file, args.distance_threshold)