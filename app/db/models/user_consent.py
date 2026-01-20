import uuid
from sqlalchemy import UUID, Column, ForeignKey, Integer, String
from app.db.base_class import Base
from app.db.timestamp import TimestampMixin
from sqlalchemy.orm import relationship


class UserConsent(Base, TimestampMixin):
    __tablename__ = "user_consents"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    client_id = Column(String, ForeignKey("oauth_clients.client_id"))

    user = relationship("User", back_populates="consents")
