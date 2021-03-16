import argparse


def _generate_sample_genotype_file(sample_mapping_csv, sample_genotypes_filepath):
    isolate_to_tracking = {}
    with open(sample_mapping_csv, "r") as f:
        for line in f:
            isolate, experiment, tracking = line.strip().split(',', maxsplit=2)
            isolate_to_tracking[isolate.strip()] = tracking.strip()

    with open(sample_genotypes_filepath, "r") as f:
        for line in f:
            isolate, genotypes = line.rstrip().split('\t', maxsplit=1)
            if isolate not in isolate_to_tracking:
                continue
            print(f"{isolate_to_tracking[isolate]}\t{isolate_to_tracking[isolate]}")


parser = argparse.ArgumentParser(description="Generate sample genotypes for uploading to redis")
parser.add_argument('sample_mapping_csv', type=str, help='Path to the sample mapping csv')
parser.add_argument('sample_genotypes_filepath', type=str, help='Path to the sample genotypes file')

if __name__ == '__main__':
    args = parser.parse_args()
    _generate_sample_genotype_file(args.sample_mapping_csv, args.sample_genotypes_filepath)
