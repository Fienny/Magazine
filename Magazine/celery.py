import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Magazine.settings')

app = Celery('Magazine')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'clear_board_every_minute': {
        'task': 'news.tasks.notify_subscribers_weekly',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
        # 'schedule': crontab(),
    },
}

app.autodiscover_tasks()
