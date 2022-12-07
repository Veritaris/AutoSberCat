import celery as celery

from app import users
from app.SberCatClient import SberCatClient
from app.config import settings
from celery.schedules import crontab

app = celery.Celery(
    "tasks",
    broker=f"redis://{settings.redis_connection_string}"
)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=2),
        renew.s(),
    )


@app.task
def renew():
    tokens = users.get_users_for_auto_sync()
    for token in tokens:
        sbercat_client = SberCatClient(token=token)
        sbercat_client.renew_all_cats_sync()
