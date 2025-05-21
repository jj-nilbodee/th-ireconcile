"""
Reflex configuration file.
"""

import reflex as rx

config = rx.Config(
    app_name="th_ireconcile",
    # port=7001,  # Changed from default 8000 to avoid blocked ports
    # api_url="http://localhost:7001/api",  # Full URL with hostname for the API
    # backend_port=7001,  # Ensure backend and frontend use the same port
)
