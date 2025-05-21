## Actual Integrated App Structure

```
th-ireconcile/
├── .github/
│   ├── instructions/
│   │   └── th-ireconcile.instructions.md
│   └── workflows/
│       ├── azure-deploy.yml
│       ├── backend-ci-cd.yml
│       └── frontend-ci-cd.yml
├── backend/                # Original backend (maintained for reference)
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   └── models/
│   │   ├── core/
│   │   ├── services/
│   │   └── tests/
│   └── ...
├── frontend/               # Original frontend (maintained for reference)
│   ├── text_compare/
│   │   ├── components/
│   │   ├── core/
│   │   ├── pages/
│   │   ├── styles/
│   │   └── utils/
│   └── ...
├── th_ireconcile/          # New integrated application
│   ├── __init__.py
│   ├── th_ireconcile.py    # Main app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py       # Integrated API routes
│   ├── components/
│   │   ├── __init__.py
│   │   ├── comparison_result.py
│   │   └── file_upload.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py       # Unified configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py      # Data models
│   ├── pages/
│   │   ├── __init__.py
│   │   └── index.py        # Main page with app state
│   ├── services/
│   │   ├── __init__.py
│   │   ├── azure_blob.py   # Azure Blob Storage service
│   │   ├── azure_ocr.py    # Azure OCR service
│   │   └── text_compare.py # Text comparison logic
│   └── styles/
│       ├── __init__.py
│       └── colors.py       # Color scheme
├── Dockerfile              # Unified Docker build
├── docker-compose.yml      # Updated to use single container
├── rxconfig.py             # Root Reflex config
├── requirements.txt        # Dependencies for Docker deployment
├── pyproject.toml          # Poetry configuration for development
├── .env.example            # Template for environment variables
├── integrated_app.md       # This documentation
├── project_structure.md
└── README.md
```

## Architecture Design

In this integrated structure:

1. **Single Container Architecture**:
   - Frontend and backend are combined into a single Reflex application
   - Both UI and API endpoints run in the same process
   - Eliminates cross-origin issues and simplifies deployment

2. **API Integration**:
   - API endpoints are implemented within Reflex using its built-in FastAPI integration
   - Routes are exposed under the `/api` prefix
   - Same processing logic is maintained from the original backend

3. **Service Integration**:
   - Azure services integration is consolidated
   - Text comparison logic is maintained
   - File handling is simplified with integrated uploads

4. **Unified Configuration**:
   - Single environment configuration using Pydantic
   - Shared settings across frontend and API components
   - Consistent error handling

5. **Deployment Benefits**:
   - Single container to deploy and maintain
   - Simplified CI/CD pipeline
   - More efficient resource utilization

The original backend and frontend directories are maintained for reference, but all active development should focus on the integrated `th_ireconcile` application.
