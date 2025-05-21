"""
Main index page of the application
"""

import reflex as rx

from th_ireconcile.api.endpoints.compare import compare_text_endpoint
from th_ireconcile.api.endpoints.extract import extract_text
from th_ireconcile.api.endpoints.upload_blob import upload_blob
from th_ireconcile.components.comparison_result import comparison_result_component
from th_ireconcile.models.schemas import ComparisonResult, TextSegment
from th_ireconcile.styles.colors import color_scheme


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
        try:
            self.is_processing = True
            self.error_message = ""

            # Check if both files are uploaded
            if not self.artwork_uploaded or not self.reference_uploaded:
                self.error_message = "Please upload both files first."
                self.is_processing = False
                return
            # Upload artwork image to extract text
            if self.artwork_image:
                # Upload image to server
                artwork_response = await upload_blob(self.artwork_image)

                # Check for upload success
                if not artwork_response or not artwork_response.image_url:
                    self.error_message = "Failed to upload artwork image."
                    self.is_processing = False
                    return
                # Now extract text from the uploaded image
                artwork_extract_response = await extract_text(
                    artwork_response.file_name, artwork_response.image_url
                )

                if (
                    not artwork_extract_response
                    or not artwork_extract_response.extracted_text
                ):
                    self.error_message = "Failed to extract text from artwork image."
                    self.is_processing = False
                    return

                self.artwork_text = artwork_extract_response.extracted_text

            # Handle reference file extraction
            if self.reference_file:
                # Process reference file based on type
                file_ext = self.reference_file.name.lower().split(".")[-1]

                if file_ext in ["html", "htm"]:
                    # Process HTML file
                    # For simplicity, we'll just read the raw HTML content
                    content = await self.reference_file.read()
                    self.reference_text = content.decode("utf-8")
                else:
                    # Treat as image and extract text
                    # Upload image to server
                    reference_response = await upload_blob(self.reference_file)

                    # Check for upload success
                    if not reference_response or not reference_response.image_url:
                        self.error_message = "Failed to upload reference file."
                        self.is_processing = False
                        return
                    # Now extract text from the uploaded image
                    reference_extract_response = await extract_text(
                        reference_response.file_name, reference_response.image_url
                    )

                    if (
                        not reference_extract_response
                        or not reference_extract_response.extracted_text
                    ):
                        self.error_message = (
                            "Failed to extract text from reference file."
                        )
                        self.is_processing = False
                        return

                    self.reference_text = reference_extract_response.extracted_text

            # Now compare the texts
            if self.artwork_text and self.reference_text:
                comparison_response = await compare_text_endpoint(
                    extracted_text=self.artwork_text,
                    reference_text=self.reference_text,
                )

                if not comparison_response:
                    self.error_message = "Failed to compare texts."
                    self.is_processing = False
                    return

                self.comparison_result = comparison_response
                self.comparison_complete = True

            self.is_processing = False
        except Exception as e:
            self.error_message = f"An error occurred: {str(e)}"
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
