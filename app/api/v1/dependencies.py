from fastapi import Request, HTTPException, status, Depends
from app.schemas.roles import Role
from app.services.user import get_current_user
from app.constants.roles import ROLE_PERMISSIONS
from typing import Callable, Union, List


def permission_required(allowed_roles: Union[Role, List[Role]] = None) -> Callable:
    if allowed_roles is not None and not isinstance(allowed_roles, list):
        allowed_roles = [allowed_roles]

    def wrapper(request: Request, current_user=Depends(get_current_user)):
        role = current_user.role
        method = request.method.upper()

        # Use the FastAPI route pattern path (e.g., /api/v1/config/{config_id})
        route_path = request.scope.get("route").path

        if allowed_roles and role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' not allowed to access this resource",
            )

        allowed = ROLE_PERMISSIONS.get(role, [])
        for rule in allowed:
            # Remove trailing slashes for comparison
            if (
                rule["url"].rstrip("/") == route_path.rstrip("/")
                and method in rule["methods"]
            ):
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{role}' not allowed to access {method} {route_path}",
        )

    return wrapper
