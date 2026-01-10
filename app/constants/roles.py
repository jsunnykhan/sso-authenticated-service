from app.schemas.roles import Role

ROLE_PERMISSIONS = {
    Role.ADMIN: [
        {"url": "/api/v1/auth/me", "methods": ["GET"]},
        {"url": "/api/v1/auth/permissions", "methods": ["GET"]},
        {"url": "/api/v1/auth/reset-password", "methods": ["POST"]},
        {"url": "/api/v1/daily-meals", "methods": ["GET"]},
        {"url": "/api/v1/daily-meals/{meal_id}", "methods": ["PUT"]},
        {"url": "/api/v1/config", "methods": ["GET", "POST"]},
        {"url": "/api/v1/config/{config_id}", "methods": ["PUT", "DELETE"]},
    ],
    Role.USER: [
        {"url": "/api/v1/auth/me", "methods": ["GET"]},
        {"url": "/api/v1/auth/permissions", "methods": ["GET"]},
        {"url": "/api/v1/auth/reset-password", "methods": ["POST"]},
        {"url": "/api/v1/daily-meals", "methods": ["GET"]},
        {"url": "/api/v1/daily-meals/{meal_id}", "methods": ["PATCH"]},
    ],
}
