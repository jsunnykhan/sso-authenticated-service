from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.api.v1.dependencies import permission_required
from app.db.session import get_db
from app.schemas.daily_meal import (
    DailyMealResponse,
    DailyMealUpdate,
    WeeklyMealResponse,
)
from app.schemas.response import ResponseModel
from app.services.daily_meal import get_weekly_meals_list, update_daily_meal
from app.services.user import get_current_user

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(permission_required())],
    response_model=ResponseModel[WeeklyMealResponse],
)
def get_daily_meals(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        meals = get_weekly_meals_list(id=current_user.id, db=db)
        response = WeeklyMealResponse(
            user_id=current_user.id,
            meals=[DailyMealResponse.model_validate(meal) for meal in meals],
        )
        return ResponseModel(code=200, message="Success", data=response)
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{meal_id}",
    dependencies=[Depends(permission_required())],
    response_model=ResponseModel,
)
def update(
    meal_id: UUID,
    body: DailyMealUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_daily_meal(
        user=current_user,
        meal_id=meal_id,
        is_enable=body.is_enable,
        db=db,
    )
    return ResponseModel(
        code=status.HTTP_206_PARTIAL_CONTENT,
        message="Meal updated",
    )
