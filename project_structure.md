# iReconcile-TH

```
ireconcile/
├── .github/
│   └── workflows/
│       ├── frontend-ci-cd.yml
│       └── backend-ci-cd.yml
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── compare.py
│   │   │   │   └── extract.py
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       └── schemas.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── settings.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── azure_blob.py
│   │   │   ├── azure_ocr.py
│   │   │   └── text_compare.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── conftest.py
│   │       ├── test_api.py
│   │       └── test_services.py
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── Dockerfile
│   ├── text_compare/
│   │   ├── __init__.py
│   │   ├── text_compare.py
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   └── index.py
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── file_upload.py
│   │   │   ├── text_input.py
│   │   │   └── comparison_result.py
│   │   ├── styles/
│   │   │   ├── __init__.py
│   │   │   └── colors.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── api.py
│   │   └── assets/
│   │       └── favicon.ico
│   ├── requirements.txt
│   └── pyproject.toml
├── .pre-commit-config.yaml
├── README.md
└── docker-compose.yml
```
