import argparse
import json


def _generate_nearest_leaf_csv(sample_mapping_csv, sample_nearest_leaf_filepath):
    isolate_to_tracking = {}
    with open(sample_mapping_csv, "r") as f:
        for line in f:
            isolate, experiment, tracking = line.strip().split(',', maxsplit=2)
            isolate_to_tracking[isolate.strip()] = tracking.strip()

    with open(sample_nearest_leaf_filepath, "r") as f:
        for line in f:
            isolate, leaf_json = line.strip().split('\t', maxsplit=1)
            if isolate.strip() not in isolate_to_tracking:
                continue
            leaf = json.loads(leaf_json)
            print("{},{},{}".format(isolate_to_tracking[isolate.strip()], leaf['leaf_id'].strip(), str(leaf['distance'])))


parser = argparse.ArgumentParser(description="Generate CSV for sample nearest leaf upload")
parser.add_argument('sample_mapping_csv', type=str, help='Path to the sample mapping csv')
parser.add_argument('sample_nearest_leaf_filepath', type=str, help='Path to the sample nearest leaf file')

if __name__ == '__main__':
    args = parser.parse_args()
    _generate_nearest_leaf_csv(args.sample_mapping_csv, args.sample_nearest_leaf_filepath)
