from typing import List
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from enum import Enum
from datetime import date


class WeekDay(str, Enum):
    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"


class DailyMealUpdate(BaseModel):
    is_enable: bool


class DailyMealResponse(DailyMealUpdate):
    id: UUID
    day: WeekDay
    week_start_date: date
    model_config = ConfigDict(from_attributes=True)


class WeeklyMealResponse(BaseModel):
    user_id: UUID
    meals: List[DailyMealResponse]

    model_config = ConfigDict(from_attributes=True)
