import logging
import os

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from th_ireconcile.models.schemas import ImageUploadResponse
from th_ireconcile.services.azure_blob import upload_to_blob_storage

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/upload-blob",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an image to Azure Blob Storage",
)
async def upload_blob(file: UploadFile = File(...)):
    """
    Upload an image/html file to Azure Blob Storage.

    Args:
        file: The image/html file to upload

    Returns:
        The URL of the uploaded image in Azure Blob Storage
    Raises:
        HTTPException: If upload fails
    """
    try:
        # Get file extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        file_ext = os.path.splitext(file.filename.lower())[1]
        allowed_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".gif",
            ".tiff",
            ".tif",
            ".html",
            ".htm",
        ]

        # Validate file extension
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format. Supported formats: {', '.join(allowed_extensions)}",
            )

        # Create temporary file
        # with NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        #     # Read file content
        #     content = await file.read()
        #     # Write to temp file
        #     temp_file.write(content)
        #     temp_path = temp_file.name

        temp_path = os.path.abspath(f"./uploads/{file.filename}")
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        # Upload file to Azure Blob Storage
        content_type = file.content_type
        blob_url = upload_to_blob_storage(
            file_path=temp_path,
            original_filename=file.filename,
            content_type=content_type,
        )

        # Clean up temp file
        # os.unlink(temp_path)

        # Return response
        return ImageUploadResponse(
            image_url=blob_url,
            file_name=file.filename,
        )

    except Exception as e:
        # Log error
        logger.error(f"Error uploading image: {str(e)}")
        # Clean up temp file if it exists
        if "temp_path" in locals() and os.path.exists(locals()["temp_path"]):
            os.unlink(locals()["temp_path"])
        # Raise HTTPException
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(
                status_code=500, detail=f"Failed to upload image: {str(e)}"
            ) from e
