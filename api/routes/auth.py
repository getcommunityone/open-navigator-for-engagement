"""
OAuth authentication routes - HuggingFace, Google, Facebook, GitHub
"""
import os
import httpx
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.database import get_db
from api.models import User, OAuthState
from api.auth import create_access_token, generate_state_token

# Load environment variables from .env file
load_dotenv()

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
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    
    config = OAUTH_PROVIDERS[provider]
    client_id = os.getenv(config['client_id_env'])
    
    if not client_id:
        raise HTTPException(
            status_code=500, 
            detail=f"OAuth not configured for {provider}. Missing {config['client_id_env']}"
        )
    
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
    
    # Build authorization URL
    params = {
        'client_id': client_id,
        'redirect_uri': callback_url,
        'scope': config['scope'],
        'state': state,
        'response_type': 'code',
    }
    
    auth_url = f"{config['authorize_url']}?{urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.get("/callback/{provider}", name="oauth_callback")
async def oauth_callback(
    provider: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """OAuth callback handler"""
    
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")
    
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    
    # Verify state token
    oauth_state = db.query(OAuthState).filter(
        OAuthState.state_token == state,
        OAuthState.provider == provider
    ).first()
    
    if not oauth_state or oauth_state.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired state token")
    
    config = OAUTH_PROVIDERS[provider]
    client_id = os.getenv(config['client_id_env'])
    client_secret = os.getenv(config['client_secret_env'])
    
    # Build callback URL (must match the one sent to authorize)
    from fastapi import Request
    # We need to reconstruct the callback URL - for now use a simple approach
    base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
    callback_url = f"{base_url}/auth/callback/{provider}"
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            config['token_url'],
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'redirect_uri': callback_url,
                'grant_type': 'authorization_code',
            },
            headers={'Accept': 'application/json'}
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=400, 
                detail=f"Token exchange failed: {token_response.text}"
            )
        
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Get user info from provider
        user_info = await get_user_info(provider, access_token, config)
    
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
    jwt_token = create_access_token(data={"sub": user.id})
    
    # Redirect to frontend with token
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    redirect_url = oauth_state.redirect_uri or frontend_url
    
    # Append token as URL parameter
    params = urlencode({'token': jwt_token})
    return RedirectResponse(url=f"{redirect_url}?{params}")


async def get_user_info(provider: str, access_token: str, config: dict) -> dict:
    """Get user information from OAuth provider"""
    
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f'Bearer {access_token}'}
        
        user_info = {}
        
        if provider == 'huggingface':
            resp = await client.get(config['userinfo_url'], headers=headers)
            data = resp.json()
            user_info = {
                'email': data.get('email'),
                'oauth_id': str(data.get('id')),
                'full_name': data.get('fullname') or data.get('name'),
                'avatar_url': data.get('avatarUrl'),
                'username': data.get('name'),
            }
        
        elif provider == 'google':
            resp = await client.get(config['userinfo_url'], headers=headers)
            data = resp.json()
            user_info = {
                'email': data.get('email'),
                'oauth_id': data.get('id'),
                'full_name': data.get('name'),
                'avatar_url': data.get('picture'),
                'username': data.get('email', '').split('@')[0],
            }
        
        elif provider == 'facebook':
            resp = await client.get(config['userinfo_url'], headers={'Authorization': f'Bearer {access_token}'})
            data = resp.json()
            user_info = {
                'email': data.get('email'),
                'oauth_id': str(data.get('id')),
                'full_name': data.get('name'),
                'avatar_url': data.get('picture', {}).get('data', {}).get('url') if isinstance(data.get('picture'), dict) else None,
                'username': data.get('name', '').replace(' ', '_').lower(),
            }
        
        elif provider == 'github':
            # Get user profile
            resp = await client.get(config['userinfo_url'], headers=headers)
            data = resp.json()
            
            # Get user email if not public
            email = data.get('email')
            if not email:
                resp_emails = await client.get('https://api.github.com/user/emails', headers=headers)
                emails = resp_emails.json()
                email = next((e['email'] for e in emails if e.get('primary')), emails[0]['email'] if emails else None)
            
            user_info = {
                'email': email,
                'oauth_id': str(data.get('id')),
                'full_name': data.get('name'),
                'avatar_url': data.get('avatar_url'),
                'username': data.get('login'),
            }
        
        return user_info


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
