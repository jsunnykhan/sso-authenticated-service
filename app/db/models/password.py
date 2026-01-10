
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base_class import Base
from app.db.timestamp import TimestampMixin

class Password(Base, TimestampMixin):
    __tablename__ = "passwords"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    algorithm = Column(String, nullable=False)
    salt = Column(String, nullable=True)
    password = Column(String, nullable=False)

    user = relationship("User", back_populates="password")
