"""
OAuth authentication routes - HuggingFace, Google, Facebook, GitHub
"""
import os
import httpx
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.database import get_db
from api.models import User, OAuthState
from api.auth import create_access_token, generate_state_token

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth provider configurations
OAUTH_PROVIDERS = {
    'huggingface': {
        'authorize_url': 'https://huggingface.co/oauth/authorize',
        'token_url': 'https://huggingface.co/oauth/token',
        'userinfo_url': 'https://huggingface.co/api/whoami-v2',
        'scope': 'openid profile email',
        'client_id_env': 'HUGGINGFACE_CLIENT_ID',
        'client_secret_env': 'HUGGINGFACE_CLIENT_SECRET',
    },
    'google': {
        'authorize_url': 'https://accounts.google.com/o/oauth2/v2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'userinfo_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
        'scope': 'openid email profile',
        'client_id_env': 'GOOGLE_CLIENT_ID',
        'client_secret_env': 'GOOGLE_CLIENT_SECRET',
    },
    'facebook': {
        'authorize_url': 'https://www.facebook.com/v18.0/dialog/oauth',
        'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
        'userinfo_url': 'https://graph.facebook.com/me?fields=id,name,email,picture',
        'scope': 'email public_profile',
        'client_id_env': 'FACEBOOK_APP_ID',
        'client_secret_env': 'FACEBOOK_APP_SECRET',
    },
    'github': {
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'userinfo_url': 'https://api.github.com/user',
        'scope': 'user:email',
        'client_id_env': 'GITHUB_CLIENT_ID',
        'client_secret_env': 'GITHUB_CLIENT_SECRET',
    },
}


# Response models
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    oauth_provider: Optional[str]


# Helper functions
def get_or_create_user(
    db: Session,
    email: str,
    provider: str,
    oauth_id: str,
    full_name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    username: Optional[str] = None,
) -> User:
    """Get existing user or create new one from OAuth data"""
    
    # Try to find existing user by OAuth ID first
    user = db.query(User).filter(
        User.oauth_provider == provider,
        User.oauth_id == oauth_id
    ).first()
    
    if user:
        # Update user info if changed
        user.full_name = full_name or user.full_name
        user.avatar_url = avatar_url or user.avatar_url
        user.username = username or user.username
        user.last_login = datetime.utcnow()
        db.commit()
        return user
    
    # Try to find by email
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Link OAuth account to existing user
        user.oauth_provider = provider
        user.oauth_id = oauth_id
        user.full_name = full_name or user.full_name
        user.avatar_url = avatar_url or user.avatar_url
        user.username = username or user.username
        user.last_login = datetime.utcnow()
        user.is_verified = True  # OAuth emails are verified
        db.commit()
        return user
    
    # Create new user
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        avatar_url=avatar_url,
        oauth_provider=provider,
        oauth_id=oauth_id,
        is_verified=True,
        is_active=True,
        last_login=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# OAuth routes
@router.get("/login/{provider}")
async def oauth_login(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
    redirect_uri: Optional[str] = None
):
    """
    Initiate OAuth login flow
    
    Supported providers: huggingface, google, facebook, github
    """
    if provider not in ['huggingface', 'google', 'facebook', 'github']:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    
    # Generate state token for CSRF protection
    state = generate_state_token()
    
    # Store state in database
    oauth_state = OAuthState(
        state_token=state,
        provider=provider,
        redirect_uri=redirect_uri,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.add(oauth_state)
    db.commit()
    
    # Build callback URL
    callback_url = str(request.url_for('oauth_callback', provider=provider))
    
    # Redirect to OAuth provider
    client = getattr(oauth, provider)
    return await client.authorize_redirect(request, callback_url, state=state)


@router.get("/callback/{provider}", name="oauth_callback")
async def oauth_callback(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """OAuth callback handler"""
    
    # Get OAuth client
    client = getattr(oauth, provider)
    
    # Exchange code for token
    try:
        token = await client.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")
    
    # Verify state token
    state = request.query_params.get('state')
    oauth_state = db.query(OAuthState).filter(
        OAuthState.state_token == state,
        OAuthState.provider == provider
    ).first()
    
    if not oauth_state or oauth_state.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired state token")
    
    # Get user info from provider
    user_info = None
    
    if provider == 'huggingface':
        resp = await client.get('https://huggingface.co/api/whoami-v2', token=token)
        data = resp.json()
        user_info = {
            'email': data.get('email'),
            'oauth_id': data.get('id'),
            'full_name': data.get('fullname') or data.get('name'),
            'avatar_url': data.get('avatarUrl'),
            'username': data.get('name'),
        }
    
    elif provider == 'google':
        user_info_dict = token.get('userinfo')
        user_info = {
            'email': user_info_dict.get('email'),
            'oauth_id': user_info_dict.get('sub'),
            'full_name': user_info_dict.get('name'),
            'avatar_url': user_info_dict.get('picture'),
            'username': user_info_dict.get('email').split('@')[0],
        }
    
    elif provider == 'facebook':
        resp = await client.get(
            'https://graph.facebook.com/me?fields=id,name,email,picture',
            token=token
        )
        data = resp.json()
        user_info = {
            'email': data.get('email'),
            'oauth_id': data.get('id'),
            'full_name': data.get('name'),
            'avatar_url': data.get('picture', {}).get('data', {}).get('url'),
            'username': data.get('name').replace(' ', '_').lower(),
        }
    
    elif provider == 'github':
        # Get user profile
        resp = await client.get('https://api.github.com/user', token=token)
        data = resp.json()
        
        # Get user email if not public
        email = data.get('email')
        if not email:
            resp_emails = await client.get('https://api.github.com/user/emails', token=token)
            emails = resp_emails.json()
            email = next((e['email'] for e in emails if e['primary']), emails[0]['email'])
        
        user_info = {
            'email': email,
            'oauth_id': str(data.get('id')),
            'full_name': data.get('name'),
            'avatar_url': data.get('avatar_url'),
            'username': data.get('login'),
        }
    
    if not user_info or not user_info.get('email'):
        raise HTTPException(status_code=400, detail="Could not retrieve user email from provider")
    
    # Get or create user
    user = get_or_create_user(
        db=db,
        email=user_info['email'],
        provider=provider,
        oauth_id=user_info['oauth_id'],
        full_name=user_info.get('full_name'),
        avatar_url=user_info.get('avatar_url'),
        username=user_info.get('username'),
    )
    
    # Clean up state token
    db.delete(oauth_state)
    db.commit()
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user.id})
    
    # Redirect to frontend with token
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    redirect_url = oauth_state.redirect_uri or frontend_url
    
    # Append token as URL parameter
    params = urlencode({'token': access_token})
    return RedirectResponse(url=f"{redirect_url}?{params}")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current authenticated user info"""
    
    # Get token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(' ')[1]
    
    # Decode token and get user
    from api.auth import decode_access_token
    payload = decode_access_token(token)
    user_id = payload.get('sub')
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/logout")
def logout():
    """Logout endpoint (client-side token removal)"""
    return {"message": "Logged out successfully. Please remove the token from client."}
