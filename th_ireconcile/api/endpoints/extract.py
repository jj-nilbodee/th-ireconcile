import logging

from fastapi import APIRouter, HTTPException, status

from th_ireconcile.core.config import get_settings
from th_ireconcile.models.schemas import TextExtractionResponse
from th_ireconcile.services.azure_ocr import extract_text_from_image

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


@router.post(
    "/extract-text",
    response_model=TextExtractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract text from an image",
)
async def extract_text(file_name: str, image_url: str):
    """
    Extract text from an image using Azure OCR.

    Args:
        image: The image file to extract text from

    Returns:
        The extracted text

    Raises:
        HTTPException: If the text extraction fails
    """
    try:
        # Extract text from the image
        extracted_text = extract_text_from_image(file_name)

        # Return the extracted text
        return TextExtractionResponse(
            extracted_text=extracted_text,
            image_url=image_url,
        )

    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract text from image: {str(e)}",
        ) from e


### TO-DO
# @router.post("/extract-html")
