"""
Comparison results component to display differences between texts
"""

import reflex as rx

from th_ireconcile.models.schemas import ComparisonResult, TextSegment
from th_ireconcile.styles.colors import color_scheme


def comparison_result_component(
    artwork_text: str, reference_text: str, comparison_result: ComparisonResult
) -> rx.Component:
    """
    Create a comparison result component that displays the comparison between texts

    Args:
        artwork_text: The extracted artwork image text
        reference_text: The reference text
        comparison_result: The comparison result from the API

    Returns:
        A component that displays the comparison result
    """
    # We no longer need to extract data using .get()
    # Instead we'll handle it with rx.cond in the rendering functions

    # Function to get text color based on match type
    def get_color_for_match_type(match_type: str) -> str:
        return rx.cond(
            match_type == "exact",
            color_scheme["match_exact"],
            rx.cond(
                match_type == "partial",
                color_scheme["match_partial"],
                color_scheme["match_none"],
            ),
        )

    # Function to get background color for match type (consistent with legend)
    def get_background_color_for_match_type(match_type: str) -> str:
        return rx.cond(
            match_type == "exact",
            "rgba(34, 197, 94, 0.1)",  # Green background from legend
            rx.cond(
                match_type == "partial",
                "rgba(245, 158, 11, 0.1)",  # Yellow background from legend
                "rgba(239, 68, 68, 0.1)",  # Red background from legend
            ),
        )

    # Function to render a segment - will be used with rx.foreach
    def render_segment(segment: TextSegment):
        return rx.text(
            segment.text,
            display="inline",
            color=get_color_for_match_type(segment.match_type),
            bg=get_background_color_for_match_type(segment.match_type),
            font_weight=rx.cond(segment.match_type == "none", "bold", "normal"),
            padding="1",
            margin="1",
            border_radius="sm",
        )

    return rx.vstack(
        rx.heading(
            "Comparison Results", size="4", color=color_scheme["primary"]
        ),  # Stats section
        rx.hstack(
            # Exact Match Box
            rx.vstack(
                rx.text("Exact Match", font_weight="bold"),
                rx.heading(
                    f"{comparison_result.stats.exact_match_percent}%",
                    size="3",
                ),
                rx.text(
                    f"{comparison_result.stats.exact_match_words} of {comparison_result.stats.total_words} words match exactly",
                    font_size="sm",
                ),
                border_radius="md",
                padding="4",
                bg=get_color_for_match_type("exact"),  # Light green background
                width="32%",
                align_items="center",
            ),
            # Partial Match Box
            rx.vstack(
                rx.text("Partial Match", font_weight="bold"),
                rx.heading(
                    f"{comparison_result.stats.partial_match_percent}%",
                    size="3",
                ),
                rx.text(
                    f"{comparison_result.stats.partial_match_words} of {comparison_result.stats.total_words} words partially match",
                    font_size="sm",
                ),
                border_radius="md",
                padding="4",
                bg=get_color_for_match_type("partial"),  # Light yellow background
                width="32%",
                align_items="center",
            ),
            # No Match Box
            rx.vstack(
                rx.text("No Match", font_weight="bold"),
                rx.heading(
                    f"{comparison_result.stats.no_match_percent}%",
                    size="3",
                ),
                rx.text(
                    f"{comparison_result.stats.no_match_words} of {comparison_result.stats.total_words} words have no match",
                    font_size="sm",
                ),
                border_radius="md",
                padding="4",
                bg=get_color_for_match_type("none"),  # Light red background
                width="32%",
                align_items="center",
            ),
            spacing="4",
            width="100%",
        ),
        # Tabs for original texts and comparison
        # Legend for colors
        rx.flex(
            rx.hstack(
                rx.box(
                    width="20px",
                    height="20px",
                    bg="rgba(34, 197, 94, 0.1)",
                    border_radius="md",
                ),
                rx.text("Exact match", font_size="sm"),
                margin_right="4",
            ),
            rx.hstack(
                rx.box(
                    width="20px",
                    height="20px",
                    bg="rgba(245, 158, 11, 0.1)",
                    border_radius="md",
                ),
                rx.text("Partial match", font_size="sm"),
                margin_right="4",
            ),
            rx.hstack(
                rx.box(
                    width="20px",
                    height="20px",
                    bg="rgba(239, 68, 68, 0.1)",
                    border_radius="md",
                ),
                rx.text("No match", font_size="sm"),
            ),
            wrap="wrap",
            width="100%",
            justify="center",
            padding="2",
            margin_bottom="4",
        ),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Comparison", value="comparison"),
                rx.tabs.trigger("Artwork Text", value="artwork"),
                rx.tabs.trigger("Reference Text", value="reference"),
            ),
            rx.tabs.content(
                rx.box(
                    rx.flex(
                        rx.foreach(
                            comparison_result.segments, render_segment
                        ),
                        wrap="wrap",
                    ),
                    padding="4",
                    border=f"1px solid {color_scheme['border']}",
                    border_radius="md",
                    width="100%",
                    overflow="auto",
                    max_height="500px",
                ),
                value="comparison",
            ),
            rx.tabs.content(
                rx.box(
                    rx.text(artwork_text),
                    padding="4",
                    border=f"1px solid {color_scheme['border']}",
                    border_radius="md",
                    width="100%",
                    overflow="auto",
                    max_height="500px",
                ),
                value="artwork",
            ),
            rx.tabs.content(
                rx.box(
                    rx.text(reference_text),
                    padding="4",
                    border=f"1px solid {color_scheme['border']}",
                    border_radius="md",
                    width="100%",
                    overflow="auto",
                    max_height="500px",
                ),
                value="reference",
            ),
            default_value="comparison",
            width="100%",
        ),
        spacing="4",
        width="100%",
        padding="4",
        border=f"1px solid {color_scheme['border']}",
        border_radius="md",
        margin_top="6",
        align_items="stretch",
    )
