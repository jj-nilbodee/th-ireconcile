"""
API routes for the application using Reflex API.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from th_ireconcile.api.endpoints import compare, extract, upload_blob

logger = logging.getLogger(__name__)

# Create API router
fastapi_app = FastAPI(title="iReconcile API", version="0.1.0")

# Configure CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
fastapi_app.include_router(extract.router, prefix="/api", tags=["extraction"])
fastapi_app.include_router(compare.router, prefix="/api", tags=["comparison"])
fastapi_app.include_router(upload_blob.router, prefix="/api", tags=["upload"])


# Custom OpenAPI schema
def custom_openapi():
    if fastapi_app.openapi_schema:
        return fastapi_app.openapi_schema

    openapi_schema = get_openapi(
        title="iReconcile",
        version="0.1.0",
        description="API for iReconcile",
        routes=fastapi_app.routes,
    )

    # Add custom documentation here if needed

    fastapi_app.openapi_schema = openapi_schema
    return fastapi_app.openapi_schema


fastapi_app.openapi = custom_openapi()


@fastapi_app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "ok"}
