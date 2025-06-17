import os
from redis import Redis
from rq import Worker, Queue, Connection

# Colas a escuchar
listen = ['default']
redis_url = os.getenv('REDIS_URL')  # p.ej. redis://... proporcionado por Render

if __name__ == '__main__':
    conn = Redis.from_url(redis_url)
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)), connection=conn)
        # with_scheduler=True habilita jobs programados
        worker.work(with_scheduler=True)
