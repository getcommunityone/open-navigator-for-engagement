"""
Database models for authentication and user management
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User account model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # OAuth provider info
    oauth_provider = Column(String(50), nullable=True)  # 'huggingface', 'google', 'facebook', 'github'
    oauth_id = Column(String(255), nullable=True)  # Provider-specific user ID
    
    # Authentication
    hashed_password = Column(String(255), nullable=True)  # For email/password (optional)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # User preferences (JSON stored as text)
    preferences = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<User {self.email}>"


class OAuthState(Base):
    """Temporary storage for OAuth state tokens (CSRF protection)"""
    __tablename__ = "oauth_states"
    
    id = Column(Integer, primary_key=True, index=True)
    state_token = Column(String(255), unique=True, index=True, nullable=False)
    provider = Column(String(50), nullable=False)
    redirect_uri = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<OAuthState {self.provider} - {self.state_token[:8]}...>"
