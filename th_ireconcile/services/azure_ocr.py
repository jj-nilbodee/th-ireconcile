import logging
import os

# from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.core.credentials import AzureKeyCredential

from th_ireconcile.core.config import settings

logger = logging.getLogger(__name__)


def extract_text_from_html(html_content: str) -> str:
    """
    Extract text from HTML content.
    This is a placeholder function that will extract text from HTML content.

    Args:
        html_content: The HTML content to extract text from

    Returns:
        Extracted text from the HTML content
    """
    try:
        # This is a placeholder for HTML text extraction
        # In a real implementation, you might use BeautifulSoup or another HTML parser
        # For now, we'll just return the HTML content as is
        # TODO: Implement proper HTML parsing to extract meaningful text
        return html_content
    except Exception as e:
        logger.error(f"Error extracting text from HTML: {str(e)}")
        return html_content


def extract_text_from_image(
    file_name: str,
) -> str:
    """
    Extract text from an image using Azure Computer Vision OCR.

    This function uses the Azure Form Recognizer API (Read API) which supports
    multiple languages including English and Thai.

    Args:
        image_url: URL of the image to extract text from

    Returns:
        Extracted text from the image

    Raises:
        Exception: If text extraction fails
    """
    try:
        # Initialize the Document Analysis client
        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=settings.AZURE_OCR_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_OCR_API_KEY),
        )

        # Start the text recognition process
        file_path = os.path.abspath(f".\\uploads\\{file_name}")
        with open(file_path, "rb") as f:
            poller = document_intelligence_client.begin_analyze_document(
                "prebuilt-layout", body=f
            )

        # Wait for the operation to complete
        result: AnalyzeResult = poller.result()

        # Extract and concatenate the text
        extracted_text = ""
        for page in result.pages:
            for line in page.lines:
                extracted_text += line.content + "\n"

        # Remove extra newlines and strip
        extracted_text = extracted_text.strip()

        logger.info(
            "Successfully extracted text from image (auto language detection for Thai and English)"
        )

        return extracted_text
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        raise Exception(f"Failed to extract text from image: {str(e)}") from e
