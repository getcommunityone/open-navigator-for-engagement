"""
Data deletion endpoints for OAuth provider compliance (Facebook, etc.)
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger
import hmac
import hashlib
import base64
import json
import os
from datetime import datetime

from api.database import get_db
from api.models import User

router = APIRouter()

class DataDeletionRequest(BaseModel):
    """Data deletion request from OAuth provider"""
    signed_request: str  # Facebook's signed request


class DataDeletionResponse(BaseModel):
    """Response to data deletion request"""
    url: str
    confirmation_code: str


def parse_signed_request(signed_request: str, app_secret: str) -> dict:
    """
    Parse and validate Facebook's signed_request parameter.
    
    Format: base64url(signature).base64url(payload)
    """
    try:
        encoded_sig, payload = signed_request.split('.', 1)
        
        # Decode signature
        sig = base64.urlsafe_b64decode(encoded_sig + '==')  # Add padding
        
        # Decode payload
        data = json.loads(base64.urlsafe_b64decode(payload + '=='))
        
        # Verify signature
        expected_sig = hmac.new(
            app_secret.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        if sig != expected_sig:
            raise ValueError("Invalid signature")
        
        return data
    except Exception as e:
        logger.error(f"Error parsing signed_request: {e}")
        raise HTTPException(status_code=400, detail="Invalid signed request")


@router.post("/data-deletion/facebook", response_model=DataDeletionResponse)
async def facebook_data_deletion_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Facebook Data Deletion Request Callback
    
    Facebook requires apps to provide a data deletion callback URL.
    This endpoint receives deletion requests and processes them.
    
    Docs: https://developers.facebook.com/docs/development/create-an-app/app-dashboard/data-deletion-callback
    """
    # Get signed_request from form data
    form = await request.form()
    signed_request = form.get("signed_request")
    
    if not signed_request:
        raise HTTPException(status_code=400, detail="Missing signed_request")
    
    # Get Facebook app secret
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    if not app_secret:
        logger.error("FACEBOOK_APP_SECRET not configured")
        raise HTTPException(status_code=500, detail="Server configuration error")
    
    # Parse and validate signed request
    data = parse_signed_request(signed_request, app_secret)
    user_id = data.get("user_id")  # Facebook user ID
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id in signed request")
    
    logger.info(f"Data deletion request from Facebook user: {user_id}")
    
    # Find user by OAuth provider ID
    user = db.query(User).filter(
        User.oauth_provider == "facebook",
        User.oauth_id == user_id
    ).first()
    
    if user:
        # Delete user data
        logger.info(f"Deleting user account: {user.email} (Facebook ID: {user_id})")
        db.delete(user)
        db.commit()
        status = "deleted"
    else:
        logger.info(f"No user found for Facebook ID: {user_id}")
        status = "not_found"
    
    # Generate confirmation code (can be used for tracking)
    confirmation_code = f"DEL-{user_id}-{int(datetime.now().timestamp())}"
    
    # Return deletion status URL
    # Users will be redirected here to see status
    base_url = os.getenv("FRONTEND_URL", "https://www.communityone.com")
    status_url = f"{base_url}/data-deletion-status?code={confirmation_code}&status={status}"
    
    logger.info(f"Data deletion request processed: {confirmation_code}")
    
    return DataDeletionResponse(
        url=status_url,
        confirmation_code=confirmation_code
    )


@router.get("/data-deletion/status")
async def data_deletion_status(code: str = None, status: str = None):
    """
    Data deletion status page (informational)
    
    Users are redirected here after Facebook processes their deletion request.
    """
    return {
        "confirmation_code": code,
        "status": status,
        "message": "Your data deletion request has been processed." if status == "deleted" else "No account found.",
        "timestamp": datetime.now().isoformat()
    }
