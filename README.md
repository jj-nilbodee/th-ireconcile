# TH-iReconcile

A web application that extracts text from images using Azure OCR and compares it with provided reference text. The comparison results are displayed with color-coded highlighting: green for exact matches, yellow for partial matches, and red for no matches.

## Features

- Image text extraction using Azure Computer Vision OCR API
- Automatic processing for both English and Thai languages
- Text comparison with color-coded results
- Image storage in Azure Blob Storage
- Integrated Reflex frontend and backend
- Spring pastel color palette dark UI

## Architecture

- **Application**: Python 3.12 with Reflex 0.7.11 (integrated API)
- **Storage**: Azure Blob Storage
- **OCR Service**: Azure Computer Vision
- **Deployment**: Azure App Service (containerized)
- **CI/CD**: GitHub Actions

## Requirements

- **Python**: 3.12 or higher
- **Azure Account**: For OCR and storage services
- **Docker**: For containerized deployment (optional)

## Local Development

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/th-ireconcile.git
   cd th-ireconcile
   ```

2. Install pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

3. Create a `.env` file in the root directory (use the `.env.example` as a template):
   ```
   AZURE_OCR_API_KEY=your_azure_ocr_api_key
   AZURE_OCR_ENDPOINT=your_azure_ocr_endpoint
   AZURE_STORAGE_CONNECTION_STRING=your_storage_connection_string
   AZURE_STORAGE_CONTAINER_NAME=uploads
   DEBUG=False
   PORT=8080
   ```

### Running the Application

#### Using Poetry for Development

```bash
# Install dependencies
poetry install

# Run the application
poetry run reflex run
```

The application will be available at http://localhost:8080

#### Using Docker (Recommended)

```bash
docker-compose up
```

The application will be available at http://localhost:8080

#### Using Poetry (Development)

```bash
cd th-ireconcile
poetry install
poetry run reflex run
```

### Dependency Management

This project supports two dependency management approaches:

#### Option 1: Using Poetry (Recommended)

1. Install Poetry if you don't have it already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies with Poetry:
   ```bash
   # For backend
   cd backend
   poetry install

   # For frontend
   cd frontend
   poetry install
   ```

#### Option 2: Using pip with requirements.txt

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies with pip:
   ```bash
   # For backend
   cd backend
   pip install -r requirements.txt

   # For frontend
   cd frontend
   pip install -r requirements.txt
   ```

**Note**: The project uses Poetry as the primary dependency manager, and requirements.txt files are automatically generated from pyproject.toml using pre-commit hooks.

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a `.env` file with your Azure credentials:
   ```
   AZURE_VISION_KEY=your_vision_key
   AZURE_VISION_ENDPOINT=your_vision_endpoint
   AZURE_STORAGE_CONNECTION_STRING=your_storage_connection_string
   AZURE_STORAGE_CONTAINER_NAME=your_container_name
   ```

3. Run the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Create a `.env` file with your backend URL:
   ```
   BACKEND_URL=http://localhost:8000
   ```

3. Run the frontend development server:
   ```bash
   reflex run
   ```

## Docker Deployment

You can use Docker Compose to run both services locally:

```bash
docker-compose up --build
```

## Deployment to Azure

The project includes GitHub Actions workflows for CI/CD deployment to Azure. To set up:

1. Configure Azure Container Registry
2. Set up Azure App Service plans for both frontend and backend
3. Configure the following GitHub secrets:
   - AZURE_CREDENTIALS
   - AZURE_CONTAINER_REGISTRY
   - AZURE_CONTAINER_REGISTRY_USERNAME
   - AZURE_CONTAINER_REGISTRY_PASSWORD
   - AZURE_FRONTEND_APP_NAME
   - AZURE_BACKEND_APP_NAME
   - AZURE_VISION_KEY
   - AZURE_VISION_ENDPOINT
   - AZURE_STORAGE_CONNECTION_STRING
   - AZURE_STORAGE_CONTAINER_NAME

## Testing

Run backend tests:
```bash
cd backend
pytest
```

## License

[MIT License](LICENSE)
