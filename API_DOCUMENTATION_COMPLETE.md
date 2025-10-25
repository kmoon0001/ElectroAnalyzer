# 📚 ElectroAnalyzer API Documentation

## 🎯 Overview

The ElectroAnalyzer API provides comprehensive clinical documentation compliance analysis using advanced AI/ML techniques while maintaining HIPAA compliance through local processing.

## 🚀 Quick Start

### Authentication
```bash
# Login to get access token
curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Document Analysis
```bash
# Upload and analyze document
curl -X POST "http://localhost:8001/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@patient_note.pdf" \
  -F "discipline=PT" \
  -F "analysis_mode=rubric" \
  -F "strictness=standard"

# Response
{
  "task_id": "uuid-string",
  "status": "accepted",
  "message": "Analysis started"
}
```

## 📊 API Endpoints

### Health & Monitoring

#### `GET /health`
**Description**: Basic health check endpoint
**Response Time**: <50ms
**Authentication**: None required

```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T07:15:54.501431+00:00",
  "uptime_seconds": 2365.82,
  "version": "1.0.0"
}
```

#### `GET /health/detailed`
**Description**: Comprehensive system health check
**Response Time**: <200ms
**Authentication**: None required

```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T07:15:57.794211+00:00",
  "uptime_seconds": 2369.11,
  "version": "1.0.0",
  "checks": {
    "database": "healthy",
    "ai_models": "ready",
    "system_resources": "normal"
  },
  "detailed_metrics": {
    "active_connections": 113,
    "python_version": "3.13.5",
    "platform": "win32"
  }
}
```

### Document Analysis

#### `POST /analyze`
**Description**: Upload and analyze clinical document for compliance
**Response Time**: 2-10 seconds (depends on document size)
**Authentication**: Required
**Rate Limit**: 10 requests/minute

**Request**:
```bash
curl -X POST "http://localhost:8001/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "discipline=PT" \
  -F "analysis_mode=rubric" \
  -F "strictness=standard"
```

**Response**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "accepted",
  "message": "Analysis started"
}
```

#### `GET /analysis/{task_id}`
**Description**: Get analysis results
**Response Time**: <100ms
**Authentication**: Required

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "compliance_score": 0.85,
  "findings": [
    {
      "category": "subjective",
      "status": "compliant",
      "confidence": 0.92,
      "details": "Patient reports significant improvement"
    }
  ],
  "recommendations": [
    "Add pain scale assessment",
    "Include functional goals"
  ]
}
```

### User Management

#### `POST /auth/login`
**Description**: Authenticate user and get access token
**Response Time**: <200ms
**Authentication**: None required

**Request**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### `POST /auth/register`
**Description**: Register new user
**Response Time**: <300ms
**Authentication**: None required

**Request**:
```json
{
  "username": "newuser",
  "password": "securepassword",
  "is_admin": false
}
```

## 🔧 Performance Characteristics

### Response Time Targets
- **Health Endpoints**: <200ms
- **Authentication**: <300ms
- **Document Analysis**: 2-10 seconds
- **File Upload**: <5 seconds
- **Report Generation**: <3 seconds

### Throughput Limits
- **Standard Endpoints**: 100 requests/minute
- **Analysis Endpoints**: 10 requests/minute
- **Upload Endpoints**: 5 requests/minute
- **Concurrent Users**: Up to 100

### Resource Usage
- **Memory**: <10GB under normal load
- **CPU**: <80% under normal load
- **Storage**: SQLite database (~100MB typical)

## 🛡️ Security Features

### Authentication
- **JWT Tokens**: Secure token-based authentication
- **Token Expiry**: 30 minutes default
- **Password Hashing**: bcrypt with salt

### Data Protection
- **PHI Scrubbing**: Automatic sensitive data removal
- **Local Processing**: No external API calls
- **Encryption**: Data encrypted at rest and in transit
- **Audit Logging**: Complete access trail

### Rate Limiting
- **DDoS Protection**: Advanced rate limiting
- **Threat Detection**: Automatic threat identification
- **CSRF Protection**: Cross-site request forgery prevention

## 📈 Error Handling

### Standard Error Responses
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid document format",
  "details": {
    "field": "file",
    "issue": "Unsupported file type"
  },
  "timestamp": "2025-10-25T07:15:54.501431+00:00",
  "request_id": "req-12345"
}
```

### HTTP Status Codes
- **200**: Success
- **201**: Created
- **202**: Accepted (async operations)
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **422**: Validation Error
- **429**: Too Many Requests
- **500**: Internal Server Error

## 🔄 WebSocket Support

### Real-time Log Streaming
```javascript
const ws = new WebSocket('ws://localhost:8001/ws/logs?token=YOUR_TOKEN');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'log') {
    console.log(`[${data.level}] ${data.message}`);
  }
};
```

## 📋 Supported File Formats

### Document Types
- **PDF**: Clinical notes, reports
- **DOCX**: Word documents
- **TXT**: Plain text files
- **Images**: PNG, JPG (with OCR)

### File Limits
- **Maximum Size**: 50MB
- **Minimum Size**: 1KB
- **Security Scan**: All files scanned for threats

## 🎯 Clinical Disciplines

### Supported Disciplines
- **PT**: Physical Therapy
- **OT**: Occupational Therapy
- **SLP**: Speech Language Pathology
- **General**: Multi-disciplinary

### Analysis Modes
- **Rubric**: Compliance against regulatory rubrics
- **Custom**: User-defined analysis criteria
- **Comprehensive**: Full clinical analysis

## 🚀 Integration Examples

### Python Client
```python
import requests
import time

class ElectroAnalyzerClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None

    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        self.token = response.json()["access_token"]
        return self.token

    def analyze_document(self, file_path, discipline="PT"):
        headers = {"Authorization": f"Bearer {self.token}"}

        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"discipline": discipline}

            response = requests.post(
                f"{self.base_url}/analyze",
                files=files,
                data=data,
                headers=headers
            )

        return response.json()

    def get_results(self, task_id):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.base_url}/analysis/{task_id}",
            headers=headers
        )
        return response.json()

# Usage
client = ElectroAnalyzerClient()
client.login("admin", "admin123")
result = client.analyze_document("patient_note.pdf", "PT")
print(f"Analysis ID: {result['task_id']}")
```

### JavaScript Client
```javascript
class ElectroAnalyzerClient {
  constructor(baseUrl = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
    this.token = null;
  }

  async login(username, password) {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    this.token = data.access_token;
    return this.token;
  }

  async analyzeDocument(file, discipline = 'PT') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('discipline', discipline);

    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.token}` },
      body: formData
    });

    return await response.json();
  }
}

// Usage
const client = new ElectroAnalyzerClient();
await client.login('admin', 'admin123');

const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];
const result = await client.analyzeDocument(file, 'PT');
console.log('Analysis ID:', result.task_id);
```

## 🔍 Troubleshooting

### Common Issues

#### Authentication Errors
```json
{
  "error": "AUTHENTICATION_FAILED",
  "message": "Invalid username or password"
}
```
**Solution**: Verify credentials and check user account status

#### File Upload Errors
```json
{
  "error": "FILE_VALIDATION_FAILED",
  "message": "File size exceeds maximum limit"
}
```
**Solution**: Ensure file is <50MB and in supported format

#### Analysis Timeout
```json
{
  "error": "ANALYSIS_TIMEOUT",
  "message": "Analysis took longer than expected"
}
```
**Solution**: Check system resources and try with smaller document

### Performance Optimization

#### Connection Pooling
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=Retry(total=3, backoff_factor=0.3)
)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

#### Batch Processing
```python
# Process multiple documents efficiently
documents = ['doc1.pdf', 'doc2.pdf', 'doc3.pdf']
results = []

for doc in documents:
    result = client.analyze_document(doc, 'PT')
    results.append(result)

# Wait for all analyses to complete
for result in results:
    while True:
        status = client.get_results(result['task_id'])
        if status['status'] == 'completed':
            break
        time.sleep(1)
```

## 📊 Monitoring & Metrics

### Performance Metrics
- **Response Times**: Tracked per endpoint
- **Memory Usage**: Monitored continuously
- **CPU Usage**: Real-time monitoring
- **Error Rates**: Tracked by error type

### Health Monitoring
- **Database Status**: Connection health
- **AI Model Status**: Model availability
- **System Resources**: Memory, CPU, disk
- **External Dependencies**: Service availability

## 🔄 API Versioning

### Current Version: v1.0.0
- **Stable**: All endpoints are stable
- **Backward Compatible**: Changes maintain compatibility
- **Deprecation Policy**: 6 months notice for breaking changes

### Future Versions
- **v1.1.0**: Enhanced analytics (planned)
- **v2.0.0**: Multi-tenant support (future)

## 📞 Support

### Documentation
- **API Reference**: Available at `/docs`
- **OpenAPI Schema**: Available at `/openapi.json`
- **Integration Guide**: This document

### Contact
- **Issues**: Report via GitHub issues
- **Questions**: Contact development team
- **Emergency**: Use health endpoints for status

---

*Last Updated: 2025-10-25*
*API Version: 1.0.0*
*Documentation Version: 1.0*
