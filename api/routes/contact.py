"""
Contact routes for submitting feedback and issues via GitHub.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import httpx
import os
from loguru import logger

router = APIRouter(prefix="/api/contact", tags=["contact"])


class ContactRequest(BaseModel):
    """Contact form submission"""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the person contacting")
    email: EmailStr = Field(..., description="Email address for follow-up")
    subject: str = Field(..., min_length=1, max_length=200, description="Subject of the message")
    message: str = Field(..., min_length=10, max_length=5000, description="Detailed message")
    category: Optional[str] = Field(default="feedback", description="Type of contact: feedback, bug, feature, question")


class ContactResponse(BaseModel):
    """Response after submitting contact form"""
    success: bool
    message: str
    issue_url: Optional[str] = None


@router.post("/submit", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def submit_contact(request: ContactRequest):
    """
    Submit a contact form message as a GitHub issue.
    
    Creates an issue in the GitHub repository with the contact information.
    Requires GITHUB_TOKEN and GITHUB_REPO environment variables.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPO", "getcommunityone/open-navigator-for-engagement")
    
    if not github_token:
        logger.warning("GitHub token not configured - contact form submission failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Contact form is not configured. Please email us directly or submit an issue on GitHub."
        )
    
    # Determine label based on category
    category_labels = {
        "bug": "bug",
        "feature": "enhancement",
        "question": "question",
        "feedback": "feedback"
    }
    label = category_labels.get(request.category, "feedback")
    
    # Create issue title and body
    issue_title = f"[Contact Form] {request.subject}"
    issue_body = f"""**From:** {request.name} ({request.email})
**Category:** {request.category}

---

{request.message}

---
*This issue was automatically created from the contact form.*
"""
    
    # Create GitHub issue
    github_api_url = f"https://api.github.com/repos/{github_repo}/issues"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "title": issue_title,
        "body": issue_body,
        "labels": [label, "contact-form"]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                github_api_url,
                json=payload,
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 201:
                issue_data = response.json()
                issue_url = issue_data.get("html_url")
                logger.info(f"Contact form submitted successfully: {issue_url}")
                return ContactResponse(
                    success=True,
                    message="Thank you for contacting us! We've received your message and will get back to you soon.",
                    issue_url=issue_url
                )
            else:
                logger.error(f"GitHub API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to submit contact form. Please try again later."
                )
    
    except httpx.TimeoutException:
        logger.error("GitHub API timeout")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request timed out. Please try again."
        )
    except httpx.RequestError as e:
        logger.error(f"GitHub API request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit contact form. Please try again later."
        )
