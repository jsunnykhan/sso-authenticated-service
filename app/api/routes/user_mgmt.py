from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.routes.dependency_jwt import validate_jwt_token
from app.core.security import hash_password, verify_password
from app.services.user import get_user_by_id, get_user_by_email

app = APIRouter()

@app.post("/change-password")
async def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    user=Depends(validate_jwt_token),
    db: Session = Depends(get_db)
):
    if not verify_password(old_password, user.password.password):
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    user.password.password = hash_password(new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@app.post("/forgot-password")
async def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_email(email, db)
    if not user:
        # Don't reveal if user exists for security
        return {"message": "If an account exists with that email, a reset link will be sent."}
    
    # In a real app, generate a reset token and send email
    return {"message": "Reset link sent"}

@app.post("/update-profile")
async def update_profile(
    name: str = Form(None),
    user=Depends(validate_jwt_token),
    db: Session = Depends(get_db)
):
    if name:
        user.name = name
    db.commit()
    return {"message": "Profile updated successfully"}

@app.post("/change-email")
async def change_email(
    new_email: str = Form(...),
    user=Depends(validate_jwt_token),
    db: Session = Depends(get_db)
):
    # Check if email is already taken
    existing_user = get_user_by_email(new_email, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already taken")
    
    user.email = new_email
    db.commit()
    return {"message": "Email updated successfully"}
