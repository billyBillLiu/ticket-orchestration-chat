from typing import Any, Optional, Dict, List, Union, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

# Generic type for paginated responses
T = TypeVar('T')

""" Classes Sttructure for the ApiResponse """

class ValidationErrorDetail(BaseModel):
    # For FasiAPI validation response detail field
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Any = Field(None, description="Invalid value that was provided")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class ApiResponse(BaseModel):
    # Universal API response structure
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    # Optional fields for errors and stuff
    data: Optional[Any] = Field(None, description="Response data (for success responses)")
    error_type: Optional[str] = Field(None, description="Type of error for client handling")
    error_code: Optional[int] = Field(None, description="HTTP status code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details or pagination info")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    """ methods for creating different types of responses """
    @classmethod
    def create_success(cls, data: Any, message: str = "Success") -> "ApiResponse":
        """Create a success response"""
        return cls(
            success=True,               # True for success
            message=message,            # optional. defaults to "Success"
            data=data                   # required
        )
    
    @classmethod
    def create_error(cls, message: str, error_type: str = "ERROR", error_code: int = 400, details: Optional[Dict[str, Any]] = None) -> "ApiResponse":
        """Create an error response"""
        return cls(
            success=False,              # False for errors
            message=message,            # required
            error_type=error_type,      # optional. defaults to "ERROR"
            error_code=error_code,      # optional. defaults to 400
            details=details             # optional. defaults to None
        )
    
    @classmethod
    def create_validation_error(cls, validation_errors: List[Dict[str, Any]]) -> "ApiResponse":
        # Takes FastAPI validation error and returns a validation error repsonse in ApiResponse form
        error_details = []
        for error in validation_errors:
            # Extract field name from location
            field = ".".join(str(loc) for loc in error.get("loc", []))
            if field.startswith("body."):
                field = field[6:]  # Remove "body." prefix
                
            error_details.append(ValidationErrorDetail(
                field=field,
                message=error.get("msg", "Validation error"),
                value=error.get("input")
            ))
        
        return cls(
            success=False,
            message="Validation failed",
            error_type="VALIDATION_ERROR",
            error_code=422,
            details={"validation_errors": error_details}
        )
    
    @classmethod
    def create_paginated(cls, data: List[Any], total: int, page: int = 1, size: int = 10, message: str = "Success") -> "ApiResponse":
        # Takes a list of data, total items, page number, and page size and returns a paginated response in ApiResponse form
        total_pages = (total + size - 1) // size
        pagination = {
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
        
        return cls(
            success=True,
            message=message,
            data=data,
            details={"pagination": pagination}
        )


""" These are the global exception handlers (for when FastAPI throws an error) used in main.py"""
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # For validation errors (Code 422)
    logger.warning(f"Validation error: {exc.errors()}")
    
    response = ApiResponse.create_validation_error(exc.errors())
    return JSONResponse(
        status_code=422,
        content=response.model_dump(mode='json')
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    # For HTTP errors (Code 400, 401, 403, 404, 500)
    logger.warning(f"HTTP exception: {exc.detail}")
    
    response = ApiResponse.create_error(
        message=str(exc.detail),
        error_type="HTTP_ERROR",
        error_code=exc.status_code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(mode='json')
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # For general exceptions (Code 500)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    response = ApiResponse.create_error(
        message="Internal server error",
        error_type="INTERNAL_ERROR",
        error_code=500
    )
    return JSONResponse(
        status_code=500,
        content=response.model_dump(mode='json')
    )

"""Utility functions for common response patterns"""
def create_success_response(data: Any, message: str = "Success") -> ApiResponse:
    # Create a success response with data
    return ApiResponse.create_success(data, message)

def create_error_response(message: str, error_type: str = "ERROR", error_code: int = 400) -> ApiResponse:
    # Create an error response
    return ApiResponse.create_error(message, error_type, error_code)

def create_validation_response(validation_errors: List[Dict[str, Any]]) -> ApiResponse:
    # Create a validation error response
    return ApiResponse.create_validation_error(validation_errors)

def create_paginated_response(data: List[Any], total: int, page: int = 1, size: int = 10) -> ApiResponse:
    # Create a paginated response
    return ApiResponse.create_paginated(data, total, page, size)

"""
Example usage for registration endpoint:

Success case:
    return ApiResponse.create_success(
        data={"user": user_data},
        message="User registered successfully"
    )

Error case:
    return ApiResponse.create_error(
        message="User with this email already exists",
        error_type="USER_EXISTS"
    )

Validation error (handled by global exception handler):
FastAPI will automatically return ApiResponse with error_type="VALIDATION_ERROR"
"""