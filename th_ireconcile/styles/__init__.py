"""
Styling modules for the application.
"""

import reflex as rx

from th_ireconcile.styles.colors import color_scheme

# Define base style for the application
BASE_STYLE = {
    "font_family": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
    "background_color": color_scheme["background"],
    rx.heading: {
        "color": color_scheme["text_primary"],
        "font_weight": "600",
    },
    rx.button: {
        "shadow": "md",
        "_hover": {
            "shadow": "lg",
        },
    },
    rx.link: {
        "text_decoration": "none",
        "_hover": {
            "text_decoration": "underline",
            "color": color_scheme["primary"],
        },
    },
}
