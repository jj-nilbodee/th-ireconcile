import logging
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple

from azure.storage.blob import BlobServiceClient, ContentSettings

from th_ireconcile.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def upload_to_blob_storage(
    file_path: str,
    original_filename: str,
    content_type: Optional[str] = None,
) -> str:
    """
    Upload a file to Azure Blob Storage.

    Args:
        file_path: Path to the file to upload
        original_filename: Original name of the file
        content_type: Content type of the file (e.g., image/jpeg)

    Returns:
        URL of the uploaded file in Azure Blob Storage

    Raises:
        Exception: If upload fails
    """
    try:
        # Extract file extension
        file_extension = Path(original_filename).suffix

        # Generate a unique filename to prevent collisions
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Create a blob service client
        blob_service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )

        # Get container client
        container_client = blob_service_client.get_container_client(
            settings.AZURE_STORAGE_CONTAINER_NAME
        )

        # Create the container if it doesn't exist
        if not container_client.exists():
            logger.info(f"Creating container: {settings.AZURE_STORAGE_CONTAINER_NAME}")
            container_client.create_container(public_access="blob")

        # Get blob client
        blob_client = container_client.get_blob_client(f"ireconcile/{unique_filename}")

        # Determine content type if not provided
        if not content_type:
            # Map common file extensions to content types
            content_type_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".bmp": "image/bmp",
                ".tiff": "image/tiff",
                ".tif": "image/tiff",
                ".pdf": "application/pdf",
                ".html": "text/html",
            }
            content_type = content_type_map.get(
                file_extension.lower(), "application/octet-stream"
            )

        # Set content settings
        content_settings = ContentSettings(content_type=content_type)

        # Upload the file
        with open(file_path, "rb") as data:
            blob_client.upload_blob(
                data, content_settings=content_settings, overwrite=True
            )

        # Get the URL of the uploaded file
        blob_url = blob_client.url

        logger.info(f"File uploaded successfully to {blob_url}")

        return blob_url
    except Exception as e:
        logger.error(f"Error uploading file to Azure Blob Storage: {str(e)}")
        raise Exception(f"Failed to upload file to Azure Blob Storage: {str(e)}") from e


def delete_from_blob_storage(blob_url: str) -> None:
    """
    Delete a file from Azure Blob Storage.

    Args:
        blob_url: URL of the file to delete

    Raises:
        Exception: If deletion fails
    """
    try:
        # Extract blob name from URL
        blob_name = blob_url.split("/")[-1]

        # Create a blob service client
        blob_service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )

        # Get container client
        container_client = blob_service_client.get_container_client(
            settings.AZURE_STORAGE_CONTAINER_NAME
        )

        # Delete the blob
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()

        logger.info(f"File deleted successfully from {blob_url}")
    except Exception as e:
        logger.error(f"Error deleting file from Azure Blob Storage: {str(e)}")
        raise Exception(
            f"Failed to delete file from Azure Blob Storage: {str(e)}"
        ) from e


async def save_upload_file(upload_file, upload_dir: str = None) -> Tuple[str, str]:
    """
    Save an uploaded file to a temporary location.

    Args:
        upload_file: FastAPI/Reflex UploadFile
        upload_dir: Directory to save the file

    Returns:
        Tuple containing (file_path, content_type)

    Raises:
        Exception: If saving fails
    """
    try:
        if upload_dir is None:
            upload_dir = settings.UPLOAD_DIR

        # Create the upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)

        # Generate a temporary file path
        file_path = os.path.join(
            upload_dir, f"{uuid.uuid4()}{Path(upload_file.filename).suffix}"
        )

        # Read the file content
        content = await upload_file.read()

        # Write the content to the temporary file
        with open(file_path, "wb") as temp_file:
            temp_file.write(content)

        return file_path, upload_file.content_type
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}")
        raise Exception(f"Failed to save uploaded file: {str(e)}") from e
