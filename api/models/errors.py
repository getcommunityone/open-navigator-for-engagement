"""
Structured error models for API responses.

Provides user-friendly error messages with expandable technical details.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ErrorDetail(BaseModel):
    """Structured error detail with user-friendly message and technical info."""
    
    message: str = Field(
        ...,
        description="User-friendly error message"
    )
    
    error_type: str = Field(
        ...,
        description="Type of error (e.g., 'data_not_found', 'network_error', 'validation_error')"
    )
    
    technical_details: Optional[str] = Field(
        None,
        description="Technical error details for debugging (expandable in UI)"
    )
    
    suggestions: Optional[list[str]] = Field(
        None,
        description="Helpful suggestions for the user"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context (state, dataset name, etc.)"
    )


def parse_error(exception: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorDetail:
    """
    Parse an exception into a structured ErrorDetail with user-friendly message.
    
    Args:
        exception: The exception to parse
        context: Additional context (state, dataset, etc.)
    
    Returns:
        ErrorDetail with user-friendly message and technical details
    """
    error_str = str(exception)
    context = context or {}
    
    # Parse HuggingFace dataset not found errors
    if "HTTP 404 Not Found" in error_str and "huggingface.co/datasets" in error_str:
        # Extract dataset name from URL
        import re
        match = re.search(r'datasets/([^/]+/[^/]+)/', error_str)
        dataset_name = match.group(1) if match else "unknown"
        
        # Extract state from dataset name or context
        state = context.get('state', 'Unknown')
        data_type = 'bills' if 'bills' in dataset_name else 'data'
        
        return ErrorDetail(
            message=f"No {data_type} data available for {state.upper()}",
            error_type="data_not_found",
            technical_details=f"Dataset '{dataset_name}' not found on HuggingFace.\n\nFull error: {error_str}",
            suggestions=[
                f"Try a different state - we have data for 50+ states",
                f"Check /api/bills/map to see which states have {data_type} data",
                "Contact support if you believe this data should be available"
            ],
            metadata={
                "dataset": dataset_name,
                "state": state,
                "data_type": data_type
            }
        )
    
    # Parse file not found errors (local environment)
    elif "No such file or directory" in error_str or "FileNotFoundError" in error_str:
        state = context.get('state', 'Unknown')
        data_type = context.get('data_type', 'data')
        
        return ErrorDetail(
            message=f"No {data_type} available for {state.upper()}",
            error_type="data_not_found",
            technical_details=error_str,
            suggestions=[
                f"This state may not have {data_type} in our database yet",
                "Try a different state or check which states have data",
                "Data is being continuously added - check back later"
            ],
            metadata={
                "state": state,
                "data_type": data_type
            }
        )
    
    # Parse DuckDB/SQL errors
    elif "DuckDB" in error_str or "SYNTAX ERROR" in error_str or "LINE" in error_str:
        return ErrorDetail(
            message="Database query error - please check your search parameters",
            error_type="query_error",
            technical_details=error_str,
            suggestions=[
                "Try simplifying your search query",
                "Check that all parameters are valid",
                "Contact support if the issue persists"
            ],
            metadata=context
        )
    
    # Parse network/timeout errors
    elif "timeout" in error_str.lower() or "connection" in error_str.lower():
        return ErrorDetail(
            message="Network request timed out - please try again",
            error_type="network_error",
            technical_details=error_str,
            suggestions=[
                "Try again in a few seconds",
                "Check your internet connection",
                "The server may be temporarily busy"
            ],
            metadata=context
        )
    
    # Parse validation errors
    elif "validation" in error_str.lower() or "invalid" in error_str.lower():
        return ErrorDetail(
            message="Invalid request parameters",
            error_type="validation_error",
            technical_details=error_str,
            suggestions=[
                "Check that all required parameters are provided",
                "Verify parameter formats (e.g., state codes should be 2 letters)",
                "See API documentation for valid parameter values"
            ],
            metadata=context
        )
    
    # Generic error fallback
    else:
        return ErrorDetail(
            message="An unexpected error occurred",
            error_type="server_error",
            technical_details=error_str,
            suggestions=[
                "Try again in a few moments",
                "Contact support if the issue persists",
                "Check the technical details for more information"
            ],
            metadata=context
        )
