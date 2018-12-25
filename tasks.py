# The module that creates the Celery worker
# use this command to start: celery -A tasks worker --pool=eventlet --loglevel=info

from celery import Celery

url = 'amqp://guest:guest@localhost:5672'

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672',
             backend='rpc://guest:guest@localhost:5672')


@app.task
def add(x, y):
    return x + y
