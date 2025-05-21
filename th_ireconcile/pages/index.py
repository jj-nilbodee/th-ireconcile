"""
Main index page of the application
"""

import logging
import reflex as rx

from th_ireconcile.api.endpoints.compare import compare_text_endpoint
from th_ireconcile.api.endpoints.extract import extract_text
from th_ireconcile.api.endpoints.upload_blob import upload_blob
from th_ireconcile.components.comparison_result import comparison_result_component
from th_ireconcile.models.schemas import ComparisonResult, TextSegment
from th_ireconcile.styles.colors import color_scheme

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) # Basic config for logger


# Define the main app state
class AppState(rx.State):
    """
    Main application state for the text comparison app
    """

    # File upload states
    artwork_image: rx.UploadFile = None
    reference_file: rx.UploadFile = None

    # Extracted text states
    artwork_text: str = ""
    reference_text: str = ""

    # Processing states
    is_processing: bool = False
    artwork_uploaded: bool = False
    reference_uploaded: bool = False
    comparison_complete: bool = False
    error_message: str = ""

    # Result states
    comparison_result: ComparisonResult = ComparisonResult(
        segments=[],
        stats={
            "total_characters": 0,
            "exact_match_characters": 0,
            "partial_match_characters": 0,
            "no_match_characters": 0,
            "total_words": 0,
            "exact_match_words": 0,
            "partial_match_words": 0,
            "no_match_words": 0,
            "exact_match_percent": 0.0,
            "partial_match_percent": 0.0,
            "no_match_percent": 0.0,
        },
    )

    def handle_artwork_image_upload(self, files: list[rx.UploadFile]):
        """
        Handle artwork image upload - processes files from the upload component
        Files is either a list of UploadFile or None (when resetting)
        """
        if files is None:  # Reset file state when None is passed
            self.artwork_uploaded = False
            self.artwork_image = None
            return

        # Get the first file from the list (we only allow single file upload)
        if isinstance(files, list) and len(files) > 0:
            self.artwork_image = files[0]  # Take the first file
            self.artwork_uploaded = True
            self.error_message = ""

    def handle_reference_file_upload(self, files: list[rx.UploadFile]):
        """
        Handle reference file upload - processes files from the upload component
        Files is either a list of UploadFile or None (when resetting)
        """
        if files is None:  # Reset file state when None is passed
            self.reference_uploaded = False
            self.reference_file = None
            return

        # Get the first file from the list (we only allow single file upload)
        if isinstance(files, list) and len(files) > 0:
            self.reference_file = files[0]  # Take the first file
            self.reference_uploaded = True
            self.error_message = ""

    async def extract_and_compare(self):
        """
        Extract text from both files and compare them
        """
        logger.info("Starting text extraction and comparison process.")
        self.is_processing = True
        self.error_message = ""
        self.comparison_complete = False # Reset comparison state

        try:
            # Log initial file states
            logger.info(f"Artwork image: {self.artwork_image.name if self.artwork_image else 'No artwork image'}")
            logger.info(f"Reference file: {self.reference_file.name if self.reference_file else 'No reference file'}")

            # Check if both files are uploaded
            if not self.artwork_uploaded or not self.artwork_image:
                self.error_message = "Artwork image is missing or not properly uploaded."
                logger.warning(f"{self.error_message} Artwork uploaded flag: {self.artwork_uploaded}, Artwork image object: {self.artwork_image is not None}")
                self.is_processing = False
                return

            if not self.reference_uploaded or not self.reference_file:
                self.error_message = "Reference file is missing or not properly uploaded."
                logger.warning(f"{self.error_message} Reference uploaded flag: {self.reference_uploaded}, Reference file object: {self.reference_file is not None}")
                self.is_processing = False
                return

            # Upload artwork image to extract text
            logger.info(f"Uploading artwork image: {self.artwork_image.name}")
            artwork_response = await upload_blob(self.artwork_image)
            logger.info(f"Artwork upload response: {artwork_response}")

            if not artwork_response or not artwork_response.image_url:
                self.error_message = "Failed to upload artwork image."
                logger.error(f"{self.error_message} Response: {artwork_response}")
                self.is_processing = False
                return

            logger.info(f"Extracting text from artwork image: {artwork_response.file_name} at {artwork_response.image_url}")
            artwork_extract_response = await extract_text(
                artwork_response.file_name, artwork_response.image_url
            )
            logger.info(f"Artwork text extraction response: {artwork_extract_response}")

            if not artwork_extract_response or not hasattr(artwork_extract_response, 'extracted_text') or artwork_extract_response.extracted_text is None:
                self.error_message = "Failed to extract text from artwork image or extracted text is empty."
                logger.error(f"{self.error_message} Response: {artwork_extract_response}")
                self.is_processing = False
                return
            self.artwork_text = artwork_extract_response.extracted_text
            logger.info(f"Artwork extracted text (first 100 chars): {self.artwork_text[:100]}")

            # Handle reference file extraction
            logger.info(f"Processing reference file: {self.reference_file.name}")
            file_ext = self.reference_file.name.lower().split(".")[-1]
            logger.info(f"Reference file extension: {file_ext}")

            if file_ext in ["html", "htm"]:
                logger.info("Reference file is HTML. Reading content.")
                try:
                    content = await self.reference_file.read()
                    self.reference_text = content.decode("utf-8")
                    logger.info(f"Reference HTML content read (first 100 chars): {self.reference_text[:100]}")
                except Exception as read_decode_err:
                    logger.exception("Error reading or decoding HTML reference file.")
                    self.error_message = f"Error processing HTML reference file: {read_decode_err}"
                    self.is_processing = False
                    return
            else:
                logger.info("Reference file is an image or other type. Uploading for OCR.")
                reference_upload_response = await upload_blob(self.reference_file)
                logger.info(f"Reference file upload response: {reference_upload_response}")

                if not reference_upload_response or not reference_upload_response.image_url:
                    self.error_message = "Failed to upload reference file."
                    logger.error(f"{self.error_message} Response: {reference_upload_response}")
                    self.is_processing = False
                    return

                logger.info(f"Extracting text from reference file: {reference_upload_response.file_name} at {reference_upload_response.image_url}")
                reference_extract_response = await extract_text(
                    reference_upload_response.file_name, reference_upload_response.image_url
                )
                logger.info(f"Reference text extraction response: {reference_extract_response}")

                if not reference_extract_response or not hasattr(reference_extract_response, 'extracted_text') or reference_extract_response.extracted_text is None:
                    self.error_message = "Failed to extract text from reference file or extracted text is empty."
                    logger.error(f"{self.error_message} Response: {reference_extract_response}")
                    self.is_processing = False
                    return
                self.reference_text = reference_extract_response.extracted_text
                logger.info(f"Reference extracted text (first 100 chars): {self.reference_text[:100]}")

            # Now compare the texts
            if self.artwork_text and self.reference_text:
                logger.info("Both artwork and reference texts are available. Proceeding to comparison.")
                comparison_response = await compare_text_endpoint(
                    extracted_text=self.artwork_text,
                    reference_text=self.reference_text,
                )
                logger.info(f"Text comparison response: {comparison_response}")

                if not comparison_response:
                    self.error_message = "Failed to compare texts."
                    logger.error(f"{self.error_message} Response: {comparison_response}")
                    self.is_processing = False
                    return

                self.comparison_result = comparison_response
                self.comparison_complete = True
                logger.info("Comparison complete. Results stored.")
            else:
                self.error_message = "One or both texts are empty after extraction. Cannot compare."
                logger.warning(f"{self.error_message} Artwork text empty: {not self.artwork_text}, Reference text empty: {not self.reference_text}")
                # No need to set self.is_processing = False here, it's done at the end of try or in except.

            self.is_processing = False
            logger.info("Text extraction and comparison process finished successfully.")

        except Exception as e:
            logger.exception("An unexpected error occurred in extract_and_compare.")
            self.error_message = f"An unexpected error occurred: {str(e)}"
            self.is_processing = False


def index() -> rx.Component:
    """
    The main index page.
    """
    return rx.vstack(
        # Header
        rx.hstack(
            rx.heading(
                "iReconcile",
                size="1",
                color=color_scheme["primary"],
            ),
            rx.spacer(),
            rx.link(
                rx.button(
                    "About",
                    variant="ghost",
                    size="1",
                ),
                href="#",
            ),
            width="100%",
            padding="4",
            border_bottom=f"1px solid {color_scheme['background_secondary']}",
        ),
        # Main content
        rx.box(
            rx.vstack(
                rx.heading(
                    "Text Recognition & Comparison Tool",
                    size="2",
                    color=color_scheme["text_primary"],
                ),
                rx.text(
                    "Upload an artwork image and a reference file to compare the text content.",
                    color=color_scheme["text_secondary"],
                ),
                # Error message if any
                rx.cond(
                    AppState.error_message != "",
                    rx.callout(
                        text=AppState.error_message,
                        color_scheme="red",
                        variant="surface",
                        high_contrast=True,
                        size="2",
                        width="100%",
                    ),
                ),
                # File upload section
                rx.flex(
                    # Artwork Image Upload
                    rx.vstack(
                        rx.heading(
                            "Upload Artwork Image",
                            size="4",
                            color=color_scheme["primary"],
                        ),
                        rx.text(
                            "This image will be processed with OCR to extract text. Supports Thai and English.",
                            color=color_scheme["text_secondary"],
                            font_size="sm",
                        ),
                        rx.text(
                            "Supports images (JPG, PNG, etc.)",
                            font_size="sm",
                            color=color_scheme["text_secondary"],
                            font_style="italic",
                        ),
                        rx.cond(
                            AppState.artwork_uploaded,
                            rx.vstack(
                                rx.text(
                                    "File uploaded successfully!",
                                    color=color_scheme["success"],
                                ),
                                rx.button(
                                    "Remove File",
                                    on_click=lambda: AppState.handle_artwork_image_upload(
                                        None
                                    ),
                                    color_scheme="red",
                                    size="1",
                                ),
                                width="100%",
                                spacing="2",
                                padding="4",
                                align="center",
                            ),
                            rx.upload(
                                rx.vstack(
                                    rx.button(
                                        "Select File",
                                        color_scheme="blue",
                                        size="3",
                                        margin_y="4",
                                    ),
                                    rx.text(
                                        "or drag and drop files here",
                                        color=color_scheme["text_secondary"],
                                        font_size="sm",
                                    ),
                                    width="100%",
                                    height="150px",
                                    spacing="2",
                                    padding="4",
                                    justify="center",
                                    align="center",
                                ),
                                id="artwork_upload",
                                multiple=False,
                                accept={
                                    "image/*": [
                                        ".jpg",
                                        ".jpeg",
                                        ".png",
                                        ".tif",
                                        ".tiff",
                                        ".bmp",
                                    ]
                                },
                                max_files=1,
                                on_drop=AppState.handle_artwork_image_upload(
                                    rx.upload_files(upload_id="artwork_upload")
                                ),
                                border=f"2px dashed {color_scheme['primary']}",
                                border_radius="md",
                                background=color_scheme["background_secondary"],
                            ),
                        ),
                        width="100%",
                        align_items="center",
                        spacing="3",
                        padding="4",
                        border_radius="lg",
                        border=f"1px solid {color_scheme['background_secondary']}",
                    ),
                    # Reference File Upload
                    rx.vstack(
                        rx.heading(
                            "Upload Reference File",
                            size="4",
                            color=color_scheme["primary"],
                        ),
                        rx.text(
                            "Upload a reference file to compare with the extracted text.",
                            color=color_scheme["text_secondary"],
                            font_size="sm",
                        ),
                        rx.text(
                            "Supports images, HTML and text files",
                            font_size="sm",
                            color=color_scheme["text_secondary"],
                            font_style="italic",
                        ),
                        rx.cond(
                            AppState.reference_uploaded,
                            rx.vstack(
                                rx.text(
                                    "File uploaded successfully!",
                                    color=color_scheme["success"],
                                ),
                                rx.button(
                                    "Remove File",
                                    on_click=lambda: AppState.handle_reference_file_upload(
                                        None
                                    ),
                                    color_scheme="red",
                                    size="1",
                                ),
                                width="100%",
                                spacing="2",
                                padding="4",
                                align="center",
                            ),
                            rx.upload(
                                rx.vstack(
                                    rx.button(
                                        "Select File",
                                        color_scheme="blue",
                                        size="3",
                                        margin_y="4",
                                    ),
                                    rx.text(
                                        "or drag and drop files here",
                                        color=color_scheme["text_secondary"],
                                        font_size="sm",
                                    ),
                                    width="100%",
                                    height="150px",
                                    spacing="2",
                                    padding="4",
                                    justify="center",
                                    align="center",
                                ),
                                id="reference_upload",
                                multiple=False,
                                accept={
                                    "image/*": [
                                        ".jpg",
                                        ".jpeg",
                                        ".png",
                                        ".tif",
                                        ".tiff",
                                        ".bmp",
                                        ".pdf",
                                    ],
                                    "text/html": [".html", ".htm"],
                                    "text/plain": [".txt"],
                                },
                                max_files=1,
                                on_drop=AppState.handle_reference_file_upload(
                                    rx.upload_files(upload_id="reference_upload")
                                ),
                                border=f"2px dashed {color_scheme['primary']}",
                                border_radius="md",
                                background=color_scheme["background_secondary"],
                            ),
                        ),
                        width="100%",
                        align_items="center",
                        spacing="3",
                        padding="4",
                        border_radius="lg",
                        border=f"1px solid {color_scheme['background_secondary']}",
                    ),
                    direction="row",
                    spacing="4",
                    width="100%",
                ),
                # Process button
                rx.button(
                    "Extract Text & Compare",
                    color_scheme="blue",
                    size="4",
                    is_loading=AppState.is_processing,
                    is_disabled=rx.cond(
                        (AppState.artwork_uploaded & AppState.reference_uploaded)
                        is False,
                        True,
                        False,
                    ),
                    on_click=AppState.extract_and_compare,
                    width="100%",
                    margin_y="4",
                ),
                # Results section (only shown when comparison is complete)
                rx.cond(
                    AppState.comparison_complete,
                    comparison_result_component(
                        AppState.artwork_text,
                        AppState.reference_text,
                        AppState.comparison_result,
                    ),
                ),
                width="100%",
                max_width="1200px",
                spacing="6",
                align_items="stretch",
            ),
            width="100%",
            padding="6",
            display="flex",
            justify_content="center",
        ),
        # Footer
        rx.box(
            rx.text(
                "© 2025 iReconcile | Azure OCR-powered Text Comparison Tool",
                font_size="sm",
                color=color_scheme["text_secondary"],
            ),
            width="100%",
            padding="4",
            text_align="center",
            border_top=f"1px solid {color_scheme['background_secondary']}",
            margin_top="8",
        ),
        min_height="100vh",
        width="100%",
        spacing="0",
        background=color_scheme["background"],
    )
