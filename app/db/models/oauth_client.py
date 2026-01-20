from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base_class import Base
from app.db.timestamp import TimestampMixin


class OAuthClient(Base, TimestampMixin):
    __tablename__ = "oauth_clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(String, unique=True, primary_key=True)
    client_secret = Column(String, nullable=False)
    client_name = Column(String, nullable=True)
    redirect_uris = Column(String, nullable=False)
