"""
Database models for authentication, user management, and social features
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, UniqueConstraint, Float
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
    
    # Location preferences
    state = Column(String(100), nullable=True)  # US State
    county = Column(String(100), nullable=True)  # County
    city = Column(String(100), nullable=True)  # City
    school_board = Column(String(255), nullable=True)  # School board/district
    
    # Profile completion
    profile_completed = Column(Boolean, default=False)
    
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


# ============================================================================
# SOCIAL FEATURES MODELS
# ============================================================================

class Organization(Base):
    """Organizations (nonprofits, charities, government agencies, advocacy groups)"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)  # URL-friendly identifier
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    website = Column(String(500), nullable=True)
    
    # Organization type
    org_type = Column(String(50), nullable=True)  # 'nonprofit', 'government', 'advocacy', 'charity'
    
    # Location
    state = Column(String(100), nullable=True)
    county = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # Contact
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Nonprofit-specific (from IRS/ProPublica)
    ein = Column(String(20), nullable=True, index=True)  # Employer Identification Number
    ntee_code = Column(String(10), nullable=True)  # National Taxonomy of Exempt Entities
    revenue = Column(Float, nullable=True)
    
    # Social stats
    follower_count = Column(Integer, default=0)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Organization {self.name}>"


class Cause(Base):
    """Causes/Topics/Issues (oral health, housing, education, climate, etc.)"""
    __tablename__ = "causes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(500), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    
    # Category
    category = Column(String(100), nullable=True)  # 'health', 'education', 'housing', 'environment', etc.
    
    # Social stats
    follower_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Cause {self.name}>"


class Leader(Base):
    """Public leaders (elected officials, decision makers, community advocates)"""
    __tablename__ = "leaders"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=True)  # 'Mayor', 'City Council Member', 'Community Organizer'
    bio = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    
    # Position details
    position_type = Column(String(100), nullable=True)  # 'elected', 'appointed', 'advocate', 'staff'
    office = Column(String(255), nullable=True)  # 'Office of the Mayor', 'City Council District 3'
    
    # Location/Jurisdiction
    state = Column(String(100), nullable=True)
    county = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    jurisdiction = Column(String(255), nullable=True)
    
    # Contact
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)
    
    # Social media
    twitter = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    facebook = Column(String(255), nullable=True)
    
    # Social stats
    follower_count = Column(Integer, default=0)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Leader {self.name}>"


# ============================================================================
# FOLLOW RELATIONSHIPS (Many-to-Many)
# ============================================================================

class UserFollow(Base):
    """User following another user"""
    __tablename__ = "user_follows"
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='unique_user_follow'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    following_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserFollow {self.follower_id} -> {self.following_id}>"


class LeaderFollow(Base):
    """User following a leader"""
    __tablename__ = "leader_follows"
    __table_args__ = (
        UniqueConstraint('user_id', 'leader_id', name='unique_leader_follow'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    leader_id = Column(Integer, ForeignKey('leaders.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<LeaderFollow user:{self.user_id} -> leader:{self.leader_id}>"


class OrganizationFollow(Base):
    """User following an organization"""
    __tablename__ = "organization_follows"
    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='unique_org_follow'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<OrganizationFollow user:{self.user_id} -> org:{self.organization_id}>"


class CauseFollow(Base):
    """User following a cause/topic"""
    __tablename__ = "cause_follows"
    __table_args__ = (
        UniqueConstraint('user_id', 'cause_id', name='unique_cause_follow'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    cause_id = Column(Integer, ForeignKey('causes.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CauseFollow user:{self.user_id} -> cause:{self.cause_id}>"

