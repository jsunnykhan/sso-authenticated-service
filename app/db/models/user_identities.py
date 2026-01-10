
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base_class import Base
from app.db.timestamp import TimestampMixin


class UserIdentity(Base , TimestampMixin):
    __tablename__ = "user_identities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4 , nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"))
    provider_user_id = Column(String, nullable=False)
    user = relationship("User", back_populates="identities")
    provider = relationship("Provider", back_populates="identities")
