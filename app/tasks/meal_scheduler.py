from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.db.models.user import User
from app.db.models.daily_meal import DailyMeal, WeekDay
from app.db.session import SessionLocal
import uuid
from app.services.config import get_config_value
from apscheduler.schedulers.background import BackgroundScheduler


def get_week_start_date(today: date) -> date:
    # Assuming week starts on Sunday
    return (
        today - timedelta(days=today.weekday() + 1) if today.weekday() != 6 else today
    )


def create_weekly_meals():
    db: Session = SessionLocal()
    try:
        week_start = get_week_start_date(date.today())
        users = db.query(User).all()
        week_special_day = (get_config_value("week_special_day") or "monday").lower()
        for user in users:
            for day in WeekDay:
                if day.value == week_special_day:
                    continue
                exists = (
                    db.query(DailyMeal)
                    .filter_by(user_id=user.id, week_start_date=week_start, day=day)
                    .first()
                )

                if not exists:
                    meal = DailyMeal(
                        id=uuid.uuid4(),
                        user_id=user.id,
                        week_start_date=week_start,
                        day=day,
                        is_enable=False,
                    )
                    db.add(meal)

        db.commit()
        print(f"[✓] Weekly meals initialized for {week_start}")
    finally:
        db.close()


def start_meal_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        create_weekly_meals,
        "cron",
        day_of_week="sat",
        hour=0,
        minute=0,
        id="weekly_meal_job",
        replace_existing=True,
    )

    scheduler.start()
