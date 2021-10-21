import json.decoder

from greenstalk import Client
from json import loads


class Worker:
    def __init__(self, tube):
        self.tube = tube

    def run(self):
        """ Listen for beanstalkd jobs and send messages """
        with Client(('127.0.0.1', 11300)) as client:
            print("Watching {} tube".format(self.tube))
            client.watch(self.tube)
            while True:
                job = client.reserve()
                try:
                    workload = loads(job.body)

                except json.decoder.JSONDecodeError as e:
                    print("Workload must be JSON: ", e)
                    client.delete(job)
                    continue

                self.handle(workload)
                print(workload)
                client.delete(job)

    def handle(self, workload: dict):
        pass
