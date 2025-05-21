import logging

from fastapi import APIRouter, HTTPException, status

from th_ireconcile.models.schemas import ComparisonResult
from th_ireconcile.services.text_compare import compare_texts

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/compare-texts",
    response_model=ComparisonResult,
    status_code=status.HTTP_200_OK,
    summary="Compare extracted text with reference text",
)
async def compare_text_endpoint(extracted_text: str, reference_text: str):
    """
    Compare extracted text with reference text and return the comparison results.

    Args:
        request: The request containing the extracted text and reference text

    Returns:
        The comparison results with text segments and their match types

    Raises:
        HTTPException: If comparison fails
    """
    try:
        # Compare the texts
        comparison_result = compare_texts(
            extracted_text=extracted_text,
            reference_text=reference_text,
        )

        # Return the comparison results
        return comparison_result

    except Exception as e:
        logger.error(f"Error comparing texts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare texts: {str(e)}",
        ) from e
