from redis import Redis
from rq import Queue
from rq.job import Job
from rq.registry import FailedJobRegistry

REDIS_HOST = "localhost"
REDIS_PORT = 6380

conn = Redis(host=REDIS_HOST, port=REDIS_PORT)
q = Queue("default", connection=conn)
registry = FailedJobRegistry(queue=q)

job_ids = registry.get_job_ids()
print(f"jobs failed: {len(job_ids)}")

for job_id in job_ids:
    job = Job.fetch(job_id, connection=conn)
    registry.remove(job)
    q.enqueue_job(job)
    print(f"re-enfileirado: {job_id}")

print(f"fila agora: {q.count}")
