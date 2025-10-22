# 🔌 ElectroAnalyzer API Documentation

> **Comprehensive API Reference** for the ElectroAnalyzer Clinical Compliance Analysis System

## 📋 **API Overview**

The ElectroAnalyzer provides a comprehensive REST API built on FastAPI with 20+ modular routers, supporting document analysis, user management, compliance reporting, and real-time monitoring.

### **Base URLs**
- **Development**: `http://127.0.0.1:8001`
- **Production**: `https://your-domain.com`
- **API Documentation**: `http://127.0.0.1:8001/docs` (Swagger UI)
- **ReDoc**: `http://127.0.0.1:8001/redoc`

### **Authentication**
All protected endpoints require JWT authentication via the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

---

## 🔐 **Authentication & Security API**

### **POST** `/auth/token`
**User Authentication**

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### **POST** `/auth/register`
**User Registration**

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

### **POST** `/auth/refresh`
**Token Refresh**

**Headers:**
```
Authorization: Bearer <current-token>
```

### **GET** `/auth/me`
**Current User Info**

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "Administrator",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### **POST** `/auth/logout`
**User Logout**

---

## 📄 **Document Analysis API**

### **POST** `/analysis/analyze`
**Upload and Analyze Document**

**Request (multipart/form-data):**
```
file: <document-file>
discipline: "PT" | "OT" | "SLP"
analysis_mode: "lenient" | "standard" | "strict"
rubric_id: "medicare_part_b" (optional)
```

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "processing",
  "message": "Document uploaded successfully"
}
```

### **GET** `/analysis/status/{task_id}`
**Check Analysis Progress**

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "processing" | "completed" | "failed",
  "progress": 75,
  "message": "Analyzing compliance requirements...",
  "estimated_completion": "2024-01-01T12:05:00Z"
}
```

### **GET** `/analysis/results/{task_id}`
**Retrieve Analysis Results**

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "analysis": {
    "overall_score": 85.5,
    "confidence": 0.92,
    "findings": [
      {
        "category": "Medical Necessity",
        "severity": "warning",
        "description": "Treatment frequency not clearly documented",
        "recommendation": "Add specific frequency details",
        "source_text": "Patient receives therapy twice weekly...",
        "line_number": 15
      }
    ],
    "summary": "Document shows good compliance with minor improvements needed",
    "recommendations": [
      "Document treatment frequency more clearly",
      "Include specific functional goals"
    ]
  },
  "metadata": {
    "document_type": "progress_note",
    "discipline": "PT",
    "analysis_mode": "standard",
    "processing_time": 23.5,
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### **POST** `/analysis/export/{task_id}`
**Export Analysis Report**

**Request Body:**
```json
{
  "format": "pdf" | "html",
  "include_recommendations": true,
  "include_source_text": true,
  "custom_branding": {
    "organization_name": "Your Clinic",
    "logo_url": "https://example.com/logo.png"
  }
}
```

**Response:**
```json
{
  "download_url": "/downloads/report-uuid.pdf",
  "expires_at": "2024-01-01T18:00:00Z"
}
```

---

## 🤖 **Unified ML API v2**

### **POST** `/api/v2/analyze/document`
**Advanced Document Analysis**

**Request Body:**
```json
{
  "document_content": "base64-encoded-content",
  "document_type": "progress_note" | "evaluation" | "discharge_summary",
  "analysis_config": {
    "strictness_level": "standard",
    "include_confidence_scores": true,
    "enable_fact_checking": true,
    "custom_rubrics": ["medicare_part_b", "state_requirements"]
  },
  "user_context": {
    "discipline": "PT",
    "experience_level": "intermediate"
  }
}
```

### **GET** `/api/v2/system/health`
**System Health Status**

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime": 3600,
  "components": {
    "database": "healthy",
    "ai_models": "healthy",
    "cache": "healthy",
    "security": "healthy"
  },
  "metrics": {
    "memory_usage": 65.2,
    "cpu_usage": 23.1,
    "active_sessions": 5,
    "pending_analyses": 2
  }
}
```

### **GET** `/api/v2/cache/stats`
**Cache Performance Metrics**

**Response:**
```json
{
  "hit_rate": 0.87,
  "miss_rate": 0.13,
  "total_requests": 15420,
  "cache_size_mb": 245.6,
  "eviction_count": 156,
  "tiers": {
    "l1_memory": {
      "hit_rate": 0.92,
      "size_mb": 128.4
    },
    "l2_disk": {
      "hit_rate": 0.78,
      "size_mb": 117.2
    }
  }
}
```

### **POST** `/api/v2/cache/clear`
**Clear System Cache**

**Request Body:**
```json
{
  "cache_tier": "all" | "memory" | "disk",
  "confirm": true
}
```

### **POST** `/api/v2/feedback/submit`
**Submit Human Feedback**

**Request Body:**
```json
{
  "analysis_id": "uuid-string",
  "feedback_type": "accuracy" | "relevance" | "completeness",
  "rating": 1-5,
  "comments": "The analysis was helpful but missed some key points",
  "suggestions": "Consider adding more specific recommendations"
}
```

---

## 📊 **Performance Monitoring API**

### **GET** `/performance/health`
**Health Check (Public)**

**Response:**
```json
{
  "status": "healthy",
  "environment": "production",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "2.0.0"
}
```

### **GET** `/performance/metrics`
**Performance Metrics**

**Response:**
```json
{
  "api_response_time_ms": 245.6,
  "analysis_time_ms": 18500.2,
  "memory_usage_percent": 65.2,
  "cpu_usage_percent": 23.1,
  "active_connections": 12,
  "cache_hit_rate": 0.87,
  "error_rate": 0.02,
  "throughput_rpm": 156.7
}
```

### **GET** `/performance/dashboard`
**Dashboard Data**

**Response:**
```json
{
  "summary": {
    "total_analyses": 1247,
    "successful_analyses": 1198,
    "average_score": 82.3,
    "average_processing_time": 18.5
  },
  "trends": {
    "daily_analyses": [45, 52, 38, 61, 47, 55, 49],
    "average_scores": [81.2, 83.1, 79.8, 84.5, 82.1, 85.2, 83.7],
    "processing_times": [19.2, 17.8, 21.1, 16.9, 18.3, 17.2, 18.9]
  },
  "alerts": [
    {
      "type": "warning",
      "message": "High memory usage detected",
      "timestamp": "2024-01-01T11:45:00Z"
    }
  ]
}
```

### **WebSocket** `/performance/ws/metrics`
**Real-time Metrics Stream**

**Connection:**
```javascript
const ws = new WebSocket('ws://127.0.0.1:8001/performance/ws/metrics');
ws.onmessage = (event) => {
  const metrics = JSON.parse(event.data);
  console.log('Real-time metrics:', metrics);
};
```

---

## 🔒 **Security Analysis API**

### **POST** `/security/analyze`
**Security Log Analysis**

**Request Body:**
```json
{
  "log_entry": "Failed login attempt for user 'admin' from IP 192.168.1.100",
  "log_level": "warning",
  "timestamp": "2024-01-01T12:00:00Z",
  "source": "auth_service"
}
```

### **GET** `/security/metrics`
**Security Metrics**

**Response:**
```json
{
  "threat_level": "low",
  "incidents_today": 3,
  "blocked_attempts": 12,
  "failed_logins": 8,
  "suspicious_activity": 2,
  "security_score": 92.5,
  "last_incident": "2024-01-01T10:30:00Z"
}
```

### **GET** `/security/trends`
**Threat Trends**

**Response:**
```json
{
  "time_range": "7d",
  "threat_types": {
    "brute_force": 15,
    "sql_injection": 3,
    "xss_attempts": 7,
    "csrf_attempts": 2
  },
  "trend_data": {
    "daily_incidents": [2, 1, 4, 3, 1, 2, 3],
    "blocked_ips": [5, 3, 8, 6, 2, 4, 7]
  }
}
```

### **GET** `/security/incidents`
**Security Incidents**

**Response:**
```json
{
  "incidents": [
    {
      "id": "inc-001",
      "type": "brute_force",
      "severity": "medium",
      "status": "resolved",
      "description": "Multiple failed login attempts detected",
      "timestamp": "2024-01-01T10:30:00Z",
      "affected_user": "admin",
      "source_ip": "192.168.1.100",
      "actions_taken": ["IP blocked", "User notified"]
    }
  ],
  "total_count": 15,
  "page": 1,
  "per_page": 10
}
```

### **GET** `/security/reports/daily`
**Daily Security Report**

**Response:**
```json
{
  "date": "2024-01-01",
  "summary": {
    "total_events": 156,
    "security_incidents": 3,
    "threat_level": "low",
    "compliance_score": 94.2
  },
  "incidents": [
    {
      "type": "failed_login",
      "count": 8,
      "severity": "low"
    },
    {
      "type": "suspicious_request",
      "count": 2,
      "severity": "medium"
    }
  ],
  "recommendations": [
    "Consider implementing additional rate limiting",
    "Review user access patterns"
  ]
}
```

---

## 👥 **User Management API**

### **GET** `/admin/users`
**List Users**

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10)
- `search`: Search term
- `role`: Filter by role

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "full_name": "Administrator",
      "role": "admin",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-01T11:30:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10
}
```

### **POST** `/admin/users`
**Create User**

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "role": "therapist"
}
```

### **PUT** `/admin/users/{user_id}`
**Update User**

### **DELETE** `/admin/users/{user_id}`
**Delete User**

### **GET** `/admin/settings`
**System Settings**

**Response:**
```json
{
  "system": {
    "max_file_size_mb": 50,
    "allowed_file_types": ["pdf", "docx", "txt"],
    "session_timeout_minutes": 30,
    "max_concurrent_sessions": 3
  },
  "ai": {
    "model_version": "2.0.0",
    "confidence_threshold": 0.75,
    "ultra_lightweight_mode": true
  },
  "security": {
    "rate_limiting_enabled": true,
    "csrf_protection": true,
    "audit_logging": true
  }
}
```

---

## 🎓 **Education & Learning API**

### **POST** `/education/learning-path`
**Create Learning Path**

**Request Body:**
```json
{
  "competency_focus": "documentation_compliance",
  "learning_level": "beginner" | "intermediate" | "advanced",
  "analysis_findings": [
    {
      "category": "Medical Necessity",
      "severity": "warning",
      "description": "Treatment frequency not clearly documented"
    }
  ]
}
```

**Response:**
```json
{
  "learning_path_id": "lp-001",
  "title": "Medical Necessity Documentation",
  "modules": [
    {
      "id": "mod-001",
      "title": "Understanding Medical Necessity",
      "content_type": "text",
      "estimated_time": 15,
      "difficulty": "beginner"
    },
    {
      "id": "mod-002",
      "title": "Documenting Treatment Frequency",
      "content_type": "interactive",
      "estimated_time": 20,
      "difficulty": "intermediate"
    }
  ],
  "total_estimated_time": 35,
  "progress": 0
}
```

### **GET** `/education/progress/{user_id}`
**Learning Progress**

**Response:**
```json
{
  "user_id": 1,
  "completed_modules": 12,
  "total_modules": 25,
  "completion_percentage": 48.0,
  "current_learning_path": "lp-001",
  "achievements": [
    {
      "id": "ach-001",
      "name": "Documentation Master",
      "description": "Completed all documentation modules",
      "earned_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

---

## 🔄 **WebSocket Endpoints**

### **WebSocket** `/ws/analysis/{task_id}`
**Real-time Analysis Updates**

**Connection:**
```javascript
const ws = new WebSocket('ws://127.0.0.1:8001/ws/analysis/task-uuid');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Progress:', update.progress);
  console.log('Status:', update.status);
};
```

**Message Format:**
```json
{
  "task_id": "uuid-string",
  "status": "processing",
  "progress": 75,
  "message": "Analyzing compliance requirements...",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 📝 **Error Handling**

### **Standard Error Response**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": {
      "field": "password",
      "issue": "Password must be at least 12 characters"
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req-uuid"
  }
}
```

### **Common Error Codes**
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource not found)
- `422` - Unprocessable Entity (business logic errors)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error (system errors)

---

## 🔧 **Rate Limiting**

### **Rate Limits by Endpoint**

| Endpoint | Requests/Minute | Requests/Hour | Burst Limit |
|----------|----------------|---------------|-------------|
| `/auth/token` | 10 | 100 | 5 |
| `/auth/register` | 5 | 20 | 3 |
| `/analysis/analyze` | 20 | 200 | 10 |
| `/admin/settings` | 5 | 50 | 3 |
| `/performance/health` | 120 | 2000 | 50 |

### **Rate Limit Headers**
```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 15
X-RateLimit-Reset: 1640995200
```

---

## 🧪 **Testing the API**

### **Using curl**
```bash
# Authenticate
curl -X POST "http://127.0.0.1:8001/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Upload document
curl -X POST "http://127.0.0.1:8001/analysis/analyze" \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "discipline=PT" \
  -F "analysis_mode=standard"

# Check status
curl -X GET "http://127.0.0.1:8001/analysis/status/<task_id>" \
  -H "Authorization: Bearer <token>"
```

### **Using Python requests**
```python
import requests

# Authenticate
auth_response = requests.post(
    "http://127.0.0.1:8001/auth/token",
    json={"username": "admin", "password": "admin123"}
)
token = auth_response.json()["access_token"]

# Upload document
with open("document.pdf", "rb") as f:
    analysis_response = requests.post(
        "http://127.0.0.1:8001/analysis/analyze",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": f},
        data={"discipline": "PT", "analysis_mode": "standard"}
    )

task_id = analysis_response.json()["task_id"]

# Check status
status_response = requests.get(
    f"http://127.0.0.1:8001/analysis/status/{task_id}",
    headers={"Authorization": f"Bearer {token}"}
)
```

---

## 📚 **Additional Resources**

- **Interactive API Documentation**: `http://127.0.0.1:8001/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8001/redoc`
- **OpenAPI Schema**: `http://127.0.0.1:8001/openapi.json`
- **Health Check**: `http://127.0.0.1:8001/health`

---

*This API documentation is automatically generated and kept up-to-date with the latest version of ElectroAnalyzer.*
