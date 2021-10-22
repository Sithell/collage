# Нужно чтобы импортировать файлы из родительской директории (TODO пофиксить)
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import json.decoder

from greenstalk import Client
from json import loads
import config.beanstalk


class Worker:
    def __init__(self, tube):
        self.tube = tube

    def run(self):
        """ Listen for beanstalkd jobs and send messages """
        with Client((config.beanstalk.host, config.beanstalk.port)) as client:
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
