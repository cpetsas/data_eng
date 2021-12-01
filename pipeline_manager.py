import rq
import redis
from model import NetworkCreator
import time
import json

class Pipe_Q:

    def create_Q(self):
        self.r = redis.StrictRedis(host = 'localhost', port = 6379)
        self.q = rq.Queue(connection = self.r)

    def create_job(self, task_path, resource_path, dependency_path):
        processor = NetworkCreator(task_path, resource_path, dependency_path)
        job = self.q.enqueue(processor.generate_everything)

    def push_in_Q(self, task_path, resource_path, dependency_path):
        self.r.lpush('requests', json.dumps({'tasks': task_path,
                         'resources':resource_path,
                         'dependencies':dependency_path}))
        print('pushed')
    

pipeline = Pipe_Q()
pipeline.create_Q()
while True:
    time.sleep(5)
    # pipeline.create_job("Tasks.csv", "Task_dependencies.csv", "resource_assignment.csv")
    pipeline.push_in_Q("Tasks.csv", "Task_dependencies.csv", "resource_assignment.csv")