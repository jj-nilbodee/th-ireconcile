from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, HttpUrl


class LanguageEnum(str, Enum):
    """Supported languages for OCR extraction."""

    ENGLISH = "en"
    THAI = "th"


class ImageUploadResponse(BaseModel):
    """Response model for image upload."""

    image_url: HttpUrl = Field(
        ..., description="URL to the uploaded image in Azure Blob Storage"
    )
    file_name: str = Field(..., description="Original filename of the uploaded image")


class TextExtractionResponse(BaseModel):
    """Response model for extracted text from image."""

    extracted_text: str = Field(..., description="Extracted text from the image")
    image_url: HttpUrl = Field(..., description="URL of the image that was processed")
    languages: List[LanguageEnum] = Field(
        default=["en", "th"], description="Languages used for text extraction"
    )


class ComparisonRequest(BaseModel):
    """Request model for text comparison."""

    extracted_text: str = Field(..., description="Text extracted from an image")
    reference_text: str = Field(..., description="Reference text to compare against")


class MatchType(str, Enum):
    """Types of text matches."""

    EXACT = "exact"
    PARTIAL = "partial"
    NONE = "none"


class TextSegment(BaseModel):
    """Model for a segment of text with its match type."""

    text: str = Field(..., description="Segment of text")
    match_type: MatchType = Field(..., description="Type of match for this segment")


class ComparisonResult(BaseModel):
    """Model for text comparison results with segments and match statistics."""

    segments: List[TextSegment] = Field(
        ..., description="List of text segments with their match types"
    )
    stats: Dict[str, Union[int, float]] = Field(
        ...,
        description="Statistics about the comparison (match percentages, etc.)",
    )


class ErrorResponse(BaseModel):
    """Model for API error responses."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(
        None, description="Error code for machine-readable identification"
    )
