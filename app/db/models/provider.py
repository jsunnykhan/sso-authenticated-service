from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base_class import Base
from app.db.timestamp import TimestampMixin


class Provider(Base , TimestampMixin):
    __tablename__ = "providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4 , nullable=False)
    name = Column(String, unique=True, nullable=False)
    client_id = Column(String, unique=True, nullable=False)
    client_secret = Column(String, nullable=False)
    redirect_url = Column(String, nullable=True) 
    identities = relationship("UserIdentity", back_populates="provider")
