"""
Passkey model for WebAuthn credential storage.

Provides:
- Storage of WebAuthn credentials (passkeys)
- User association
- Credential metadata
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from backend.db.base import Base


class Passkey(Base):
    """
    Passkey model representing a WebAuthn credential.

    Attributes:
        id: Unique passkey identifier (UUID)
        user_id: Foreign key to User
        credential_id: Base64-encoded credential ID
        public_key: Base64-encoded public key
        counter: Signature counter (for replay protection)
        name: User-friendly name for the passkey
        last_used_at: Timestamp of last successful authentication
        created_at: Credential creation timestamp
        is_active: Whether the credential is active
    """

    __tablename__ = "passkeys"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # WebAuthn Credential Data
    credential_id = Column(Text, nullable=False, unique=True, index=True)  # Base64-encoded
    public_key = Column(Text, nullable=False)  # Base64-encoded COSE key
    counter = Column(Integer, default=0, nullable=False)  # Signature counter

    # Metadata
    name = Column(String(255))  # User-friendly name (e.g., "My iPhone", "YubiKey")
    last_used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    # user = relationship("User", back_populates="passkeys")

    def __repr__(self):
        return f"<Passkey {self.name or self.id} for user {self.user_id}>"

