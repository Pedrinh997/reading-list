from redis import Redis
from rq import Queue
import jobs

conn = Redis(host="localhost", port=6380)
q = Queue("default", connection=conn)

job = q.enqueue(jobs.processar_url, "https://exemplo1.com")
print(f"job enfileirado: {job.id}")
print(f"jobs na fila: {q.count}")
