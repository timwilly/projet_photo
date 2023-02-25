from app import scheduler
from app.tasks import import_data
from flask import current_app
from pytz import utc, timezone
from apscheduler.schedulers.background import BackgroundScheduler


class BgScheduler:
    eastern_tz = timezone('US/Eastern')
    
    @scheduler.task('cron', id='do job 1', hour=1, minute=31, second=11, 
                    misfire_grace_time=800, timezone=eastern_tz)
    def import_():
        with scheduler.app.app_context():
            import_data()