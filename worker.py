from redis import StrictRedis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

conn = StrictRedis()

if __name__ == '__main__':
	with Connection(conn):
		worker = Worker(map(Queue, listen))
		worker.work()
