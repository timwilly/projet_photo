import app.tasks
from flask import current_app
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler


class BgScheduler:
    
    def scheduler():
        try:
            scheduler = BackgroundScheduler(timezone=utc)
            scheduler.add_job(func=app.tasks.import_data, trigger='cron', hour=0)
            scheduler.start()
        except Exception as e:
            print(e)
