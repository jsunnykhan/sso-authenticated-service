from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base_class import Base
from app.db.timestamp import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)

    # Relationships
    password = relationship(
        "Password", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )
    profile = relationship(
        "UserProfile",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan",
    )
    consents = relationship("UserConsent", back_populates="user")
