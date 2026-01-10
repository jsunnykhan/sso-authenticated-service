from sqlalchemy.orm import Session
from uuid import UUID
from app.db.models.daily_meal import DailyMeal
from app.db.models.user import User


def get_weekly_meals_list(id: UUID, db: Session):
    meals = (
        db.query(DailyMeal)
        .filter(DailyMeal.user_id == id)
        .order_by(DailyMeal.week_start_date.desc())
        .all()
    )
    return meals


def update_daily_meal(
    user: User,
    meal_id: UUID,
    is_enable: bool,
    db: Session,
):
    meal = db
    pass
