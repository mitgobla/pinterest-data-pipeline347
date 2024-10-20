import yaml
import requests
import json


class KinesisAPI:
    """Provides an interface to the Kinesis Streams REST API"""
    def __init__(self, conf_file: str = "stream_api_conf.yaml"):
        """Provides an interface to the Kinesis REST API

        See `stream_api_conf.example.yaml` to see how configuration is set.
        """

        with open(conf_file, "r") as f:
            self._conf = yaml.safe_load(f)

        self.streams = self._conf["STREAMS"]
        self._invoke_url: str = self._conf["INVOKE_URL"]
        self._invoke_url = self._invoke_url if self._invoke_url.endswith("/") else self._invoke_url + "/"
        self._headers: dict = self._conf["HEADERS"]
        self._partition_key = self._conf["PARTITION_KEY"]

    def record_to_stream(self, stream: str, data: dict) -> requests.Response:
        """Send a record to a Kinesis stream

        Args:
            stream (str): The stream name
            data (dict): The data payload

        Returns:
            requests.Response: Response result from PUT call
        """
        url = f"{self._invoke_url}/streams/{stream}/record"
        payload = json.dumps({
            "StreamName": stream,
            "Data": data,
            "PartitionKey": self._partition_key
        }, default=str)

        return requests.request("PUT", url, headers=self._headers, data=payload)

    def records_to_stream(self, stream: str, data: list[dict]) -> requests.Response:
        """Send a batch of records to a Kinesis stream

        Args:
            stream (str): The stream name
            data (list[dict]): An array of data payloads

        Returns:
            requests.Response: Response result from POST call
        """
        url = f"{self._invoke_url}/streams/{stream}/records"
        records = [
            {"Data": item, "PartitionKey": self._partition_key} for item in data
        ]
        payload = json.dumps({
            "StreamName": stream,
            "Records": records
        }, default=str)
        return requests.request("POST", url, headers=self._headers, data=payload)