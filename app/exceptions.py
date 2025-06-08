from fastapi.responses import JSONResponse
from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=404, content={"message": "Not found"})

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=404, content={"message": "Validation error"})

async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=404, content={"message": "Unknown error"})
