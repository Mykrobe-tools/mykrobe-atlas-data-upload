import argparse
import json


def _generate_requests(sample_mapping_csv, sample_nearest_leaf_filepath, sample_nearest_neighbours_filepath,
                       atlas_api_host):
    isolate_to_experiment = {}
    isolate_to_tracking = {}
    isolate_to_leaf = {}
    with open(sample_mapping_csv, "r") as f:
        for line in f:
            isolate, experiment, tracking = line.strip().split(',', maxsplit=2)
            isolate_to_experiment[isolate.strip()] = experiment.strip()
            isolate_to_tracking[isolate.strip()] = tracking.strip()
    with open(sample_nearest_leaf_filepath, "r") as f:
        for line in f:
            isolate, leaf_json = line.strip().split('\t', maxsplit=1)
            leaf = json.loads(leaf_json)
            isolate_to_leaf[isolate.strip()] = leaf['leaf_id'].strip()
    with open(sample_nearest_neighbours_filepath, "r") as f:
        for line in f:
            sample, distance_data = line.strip().split('\t', maxsplit=1)
            sample = sample.strip()
            if sample not in isolate_to_tracking:
                continue
            distance_list = json.loads(distance_data)
            data = [{
                'sampleId': isolate_to_tracking[d['experiment_id'].strip()],
                'leafId': isolate_to_leaf[d['experiment_id'].strip()],
                'distance': d['distance']
            } for d in distance_list if d['experiment_id'].strip() in isolate_to_tracking]
            payload = {
                "type": "distance",
                "leafId": isolate_to_leaf[sample],
                "result": data
            }
            print('echo \'' + json.dumps(payload) +
                  '\' | curl -X POST -w "\\n" -H "Authorization: Bearer $1" -H "Content-Type: application/json" -d @- ' +
                  atlas_api_host + '/experiments/' + isolate_to_experiment[sample] + '/results')


parser = argparse.ArgumentParser(description="Generate curl requests for sample nearest neighbours cache")
parser.add_argument('sample_mapping_csv', type=str, help='Path to the sample mapping csv')
parser.add_argument('sample_nearest_leaf_filepath', type=str, help='Path to the sample nearest leaf file')
parser.add_argument('sample_nearest_neighbours_filepath', type=str, help='Path to the sample nearest neighbours file')
parser.add_argument('atlas_api_host', type=str, help='Atlas API host, e.g.: https://api-dev.mykro.be')

if __name__ == '__main__':
    args = parser.parse_args()
    _generate_requests(args.sample_mapping_csv, args.sample_nearest_leaf_filepath,
                       args.sample_nearest_neighbours_filepath, args.atlas_api_host)
