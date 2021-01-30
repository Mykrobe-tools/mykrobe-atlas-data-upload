import argparse


def _extract(included_sample_file, sample_mapping_csv):
    included_samples = set()
    with open(included_sample_file, 'r') as f:
        for line in f:
            included_samples.add(line.strip())

    with open(sample_mapping_csv, 'r') as csv:
        for line in csv:
            experiment_id, isolate_id, tracking_id = line.strip().split(',')
            if isolate_id in included_samples:
                print(f'{isolate_id},{experiment_id},{tracking_id}')
            elif experiment_id in included_samples:
                print(f'{experiment_id},{isolate_id},{tracking_id}')


parser = argparse.ArgumentParser(description='Extract sample mapping')
parser.add_argument('included_sample_file', type=str, help='Path to the included sample list')
parser.add_argument('sample_mapping_csv', type=str, help='Path to the sample mapping csv')

if __name__ == '__main__':
    args = parser.parse_args()
    _extract(args.included_sample_file, args.sample_mapping_csv)
