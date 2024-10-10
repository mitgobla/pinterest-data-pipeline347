import yaml
import requests
import json


class KafkaAPI:
    """Provides an interface to the Kafka REST API"""

    def __init__(self, conf_file: str = "api_conf.yaml"):
        """Provides an interface to the Kafka REST API

        See `api_conf.example.yaml` to see how configuration is set.
        """
        with open(conf_file, "r") as f:
            self._conf = yaml.safe_load(f)

        self.topics: dict = self._conf["TOPICS"]
        self._invoke_url: str = self._conf["INVOKE_URL"]
        self._invoke_url = self._invoke_url if self._invoke_url.endswith("/") else self._invoke_url + "/"
        self._headers: dict = self._conf["HEADERS"]

    def get_topics(self) -> tuple:
        """Return a tuple of configured topics

        Returns:
            tuple: Topic keys in the configuration file.
        """
        return tuple(self.topics.keys())

    def post_to_topic(self, topic: str, data: dict) -> requests.Response:
        url = self._invoke_url + "topics/" + topic
        payload = json.dumps({
            "records": [
                {
                    "value": data
                }
            ]
        }, default=str)
        return requests.request("POST", url, headers=self._headers, data=payload)