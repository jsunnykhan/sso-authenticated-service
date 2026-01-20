from app.db.base_class import Base
from app.db.models.oauth_client import OAuthClient
from app.db.models.user import User
from app.db.models.password import Password
from app.db.models.user_profile import UserProfile
from app.db.models.user_consent import UserConsent


# Import all models here to ensure they are registered with SQLAlchemy's Base.metadata