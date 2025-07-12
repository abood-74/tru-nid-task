# Egyptian National ID Extractor API

A Django REST API service for extracting information from Egyptian national IDs, including date of birth, gender, and governorate details.

## Features

- **ID Validation**: Validates 14-digit Egyptian national ID format
- **Data Extraction**: Extracts date of birth, gender, and governorate
- **API Key Authentication**: Secure access control
- **Token-based Usage**: Tracks API usage with token consumption
- **Rate Limiting**: 1000 requests/hour per user
- **Usage Logging**: Comprehensive API call tracking
- **Admin Interface**: User and usage management

## Setup

### Setup With Docker

1. **Clone the repository:**
   ```bash
   git clone https://github.com/abood-74/tru-nid-task.git
   cd tru-nid-task
   ```

2. **Create environment file:**
   
   Create `.env` in `env_files/` directory:
   ```bash
   POSTGRES_DB=tru_nid_db
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   SECRET_KEY=your-django-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=["localhost", "0.0.0.0", "127.0.0.1"]
   CSRF_TRUSTED_ORIGIN=['http://localhost:8000', 'http://127.0.0.1:8000']
   ```

3. **Start services:**
   ```bash
   docker-compose up --build
   ```

4. **Load test data:**
   ```bash
   docker-compose exec django python manage.py setup_test_data
   ```



### Setup Without Docker

1. **Clone and setup:**
   ```bash
   git clone https://github.com/abood-74/tru-nid-task.git
   cd tru-nid-task
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r compose/django/requirements.txt
   ```

3. **Configure environment: (Not Required)** 
   
   Create `.env` in project root:
   ```bash
   DEBUG=True 
   SECRET_KEY=your-secret-key-here
   USE_DOCKER=False
   ALLOWED_HOSTS=["localhost", "0.0.0.0", "127.0.0.1"]
   CSRF_TRUSTED_ORIGIN=['http://localhost:8000', 'http://127.0.0.1:8000']
   ```

4. **Setup database:**
   ```bash
   python manage.py setup_test_data
   ```

5. **Collect Static:**

    ```bash
   python manage.py collectstatic
   ```
  
6. **Start server:**
   ```bash
   python manage.py runserver
   ```

## API Usage

### Authentication

Include API key in request headers:
```bash
X-API-Key: your_api_key_here
```

### Endpoint

**POST** `/api/v1/national-ids/egyptian-id/extract/`

**Request:**
```json
{
  "national_id": "29001010123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "ID validation completed successfully",
  "data": {
    "national_id": "29001010123456",
    "date_of_birth": "1990-01-01",
    "governorate": "Cairo",
    "gender": "male"
  },
  "errors": null
}
```

### Example Requests

cURL:
```bash
curl -X POST http://localhost:8000/api/v1/national-ids/egyptian-id/extract/ \
     -H "X-API-Key: nid_test_key_123456789012345678901234567" \
     -H "Content-Type: application/json" \
     -d '{"national_id": "29001010123456"}'
```



## Test Data

| User | Email | Password | Tokens | API Key |
|------|-------|----------|---------|---------|
| Admin | admin@test.com | admin123 | 1000 | `nid_admin_test_key_123456789012345678901234` |
| Tester | tester@test.com | test123 | 500 | `nid_test_key_123456789012345678901234567` |
| Demo | demo@test.com | demo123 | 100 | `nid_demo_key_123456789012345678901234567` |

### Test National IDs

| National ID | Birth Date | Governorate | Gender |
|-------------|------------|-------------|---------|
| 29001010123456 | 1990-01-01 | Cairo | Male |
| 29001020223446 | 1990-01-02 | Alexandria | Female |


## Testing

Run the test suite:
```bash
# All tests
python -m pytest

# Specific test files
python -m pytest national_ids/tests/test_views.py
python -m pytest national_ids/tests/test_serializers.py

# With coverage
python -m pytest --cov=.
```

## Project Structure

```
tru-nid-task/
├── core/                    # Django configuration
│   ├── settings.py         # Main settings
│   ├── urls.py             # URL routing
│   └── utils/              # Authentication & throttling
├── national_ids/           # Main API app
│   ├── views.py           # API endpoints
│   ├── serializers.py     # Request validation
│   ├── services.py        # ID extraction logic
│   ├── constants.py       # Governorate mappings
│   └── tests/             # Test suite
├── users/                  # User & API key management
│   ├── models.py          # User, APIKey, APIUsage models
│   └── managers.py        # Custom user manager
├── fixtures/               # Test data
└── compose/                # Docker configuration
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEBUG` | Debug mode | No |
| `SECRET_KEY` | Django secret key | No |
| `USE_DOCKER` | Use Docker database | No |
|`ALLOWED_HOSTS` | Comma-separated list of allowed hostnames/IPs | NO |
| `POSTGRES_DB` | Database name | Docker only |
| `CSRF_TRUSTED_ORIGIN` | Comma-separated list of trusted origins for CSRF protection | NO
| `POSTGRES_USER` | Database user | Docker only |
| `POSTGRES_PASSWORD` | Database password | Docker only |
| `POSTGRES_HOST` | Database host | Docker only |
| `POSTGRES_PORT` | Database port | Docker only |


## URLs
- **API Base**: http://localhost:8000/api/v1/
- **Admin Panel**: http://localhost:8000/admin/

## Rate Limiting

- 1000 requests per hour per user
- Returns 429 status code when exceeded
- Includes `Retry-After` header

## Token System

- Each successful extraction costs 1 token
- Failed validation requests are free
- Tokens managed through Django admin interface

## Troubleshooting

**Port conflicts:**
```bash
python manage.py runserver 8001

```


**Reset test data:**
```bash
python manage.py flush --noinput
python manage.py setup_test_data
```
**My Logic Behind The Current Implementation**
 The current token system is designed for integration with payment gateways (Stripe/PayPal) using webhook-based automatic crediting for pay-as-you-go pricing. Plans include user registration/login endpoints and a usage dashboard for self-service account management. However, per task requirements, this implementation focuses on the core single API endpoint functionality.