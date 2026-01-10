import uuid
from enum import Enum
from datetime import date
from sqlalchemy import (
    Column,
    Boolean,
    ForeignKey,
    Enum as PgEnum,
    Date,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class WeekDay(str, Enum):
    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"


class DailyMeal(Base):
    __tablename__ = "daily_meals"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    week_start_date = Column(Date, nullable=False)
    day = Column(PgEnum(WeekDay, name="weekday_enum", create_type=True), nullable=False)

    is_enable = Column(Boolean, default=False, nullable=False)

    user = relationship("User", backref="weekly_meals")

    __table_args__ = (
        UniqueConstraint("user_id", "week_start_date", "day", name="uix_user_week_day"),
    )
