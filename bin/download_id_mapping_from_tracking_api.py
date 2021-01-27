import argparse

import tracking_client
from tracking_client import Configuration, SampleApi


def _download(isolate_id_list_filepath, tracking_api_host):
    configuration = Configuration()
    configuration.host = tracking_api_host
    api_client = tracking_client.ApiClient(configuration=configuration)

    sample_api = SampleApi(api_client)

    with open(isolate_id_list_filepath, 'r') as inf:
        for iid in inf:
            from_tracking_api = sample_api.samples_get(isolate_id=iid)

            if not from_tracking_api:
                continue

            print(f"{from_tracking_api[0].isolate_id},{from_tracking_api[0].experiment_id},{from_tracking_api[0].id}")


parser = argparse.ArgumentParser(description='Download ID mapping from Tracking API, output in CSV format')
parser.add_argument('isolate_id_list_filepath', type=str, help='Path to input file. Expects each line is an isolate ID')
parser.add_argument('tracking_api_host', type=str, help='Tracking API host, e.g.: http://tracking-api-service/api/v1')

if __name__ == '__main__':
    args = parser.parse_args()
    _download(args.isolate_id_list_filepath, args.tracking_api_host)
