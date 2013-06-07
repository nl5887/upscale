import os

from upscale import config

import datetime 
import pprint

from upscale.worker import tasks

def status():
	containers={}
        for i in tasks.get_instances():
                a=tasks.get_containers.apply_async(queue=i.id, routing_key=i.id, expires=datetime.datetime.now()+datetime.timedelta(seconds=5), )
                containers[i.id] = a.get(timeout=5)

        pprint.pprint(containers)


