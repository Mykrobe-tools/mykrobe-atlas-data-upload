import argparse


def _generate_requests(included_samples_file, sample_mapping_csv, sample_nearest_neighbours_filepath, distance_threshold):
    included_samples = []
    with open(included_samples_file, "r") as f:
        for line in f:
            isolate, _ = line.strip().split(',', maxsplit=1)
            included_samples.append(isolate)

    isolate_to_tracking = {}
    with open(sample_mapping_csv, "r") as f:
        for line in f:
            isolate, experiment, tracking = line.strip().split(',', maxsplit=2)
            isolate_to_tracking[isolate.strip()] = tracking.strip()

    with open(sample_nearest_neighbours_filepath, "r") as f:
        first_line = next(f)
        target_list = list(map(lambda x: x.strip(), first_line.rstrip().split('\t')))
        line_num = 1
        for line in f:
            line_num += 1
            distances = line.rstrip().split('\t')
            source_sample = distances[0].strip()
            if source_sample not in included_samples:
                continue
            if source_sample not in isolate_to_tracking:
                continue
            for i in range(line_num, len(distances)):
                target_sample = target_list[i]
                if target_sample not in isolate_to_tracking:
                    continue
                if distance_threshold >= int(distances[i]):
                    print(f"{isolate_to_tracking[source_sample]},{isolate_to_tracking[target_sample]},{distances[i]}")


parser = argparse.ArgumentParser(description="Generate CSV for sample nearest neighbours upload")
parser.add_argument('included_samples_file', type=str, help='Path to the included samples file, you can use the same file as mapping file')
parser.add_argument('sample_mapping_csv', type=str, help='Path to the sample mapping csv')
parser.add_argument('sample_nearest_neighbours_filepath', type=str, help='Path to the sample nearest neighbours file')
parser.add_argument('distance_threshold', type=int, help='The distance threshold for nearest neighbours')

if __name__ == '__main__':
    args = parser.parse_args()
    _generate_requests(args.included_samples_file, args.sample_mapping_csv, args.sample_nearest_neighbours_filepath, args.distance_threshold)
