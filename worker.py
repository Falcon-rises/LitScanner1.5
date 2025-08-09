from celery import Celery
import config

celery = Celery('worker', broker=config.REDIS_URL, backend=config.REDIS_URL)

# autodiscover tasks if used in package; here tasks.py is imported directly
celery.autodiscover_tasks(['tasks'])
