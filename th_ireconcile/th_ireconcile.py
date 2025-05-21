"""
Main Reflex app entry point
"""

import reflex as rx

from th_ireconcile import styles
from th_ireconcile.api.app import fastapi_app
from th_ireconcile.pages.index import index

# Create app with theme and styling
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accentColor="sky",
        grayColor="slate",
        primaryColor="sky",
    ),
    style=styles.BASE_STYLE,
    api_transformer=fastapi_app,
)

# Register API routes
# app.api.mount_routers(api_router)

# Register all pages
app.add_page(index, route="/")
