# 🚀 ElectroAnalyzer Integration Guide

## 📋 Quick Start Checklist

- [ ] **System Requirements**: Python 3.8+, Node.js 16+, 8GB RAM minimum
- [ ] **Installation**: Clone repository and install dependencies
- [ ] **Configuration**: Set up environment variables
- [ ] **Database**: Initialize SQLite database
- [ ] **Authentication**: Create admin user
- [ ] **Testing**: Run health checks
- [ ] **Deployment**: Start services

## 🛠️ Installation & Setup

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Node.js 16+ required
node --version

# Git for cloning
git --version
```

### Backend Setup
```bash
# Clone repository
git clone https://github.com/your-org/electroanalyzer.git
cd electroanalyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database.database import init_db; import asyncio; asyncio.run(init_db())"

# Start API server
python start_robust.py
```

### Frontend Setup
```bash
# Navigate to frontend
cd frontend/electron-react-app

# Install dependencies
npm install

# Start development server
npm start
```

## ⚙️ Configuration

### Environment Variables
```bash
# Create .env file
cat > .env << EOF
# Security
SECRET_KEY=your-secret-key-here
USE_AI_MOCKS=true

# Database
DATABASE_URL=sqlite:///./compliance.db

# API
HOST=127.0.0.1
PORT=8001

# Logging
LOG_LEVEL=INFO
EOF
```

### Configuration File
```yaml
# config.yaml
analysis:
  confidence_threshold: 0.75
  max_document_length: 50000

use_ai_mocks: true

auth:
  access_token_expire_minutes: 30
  algorithm: HS256

database:
  url: sqlite:///./compliance.db
  pool_size: 10
  sqlite_optimizations: true

performance:
  ultra_lightweight_mode: true
  max_ram_gb: 10.0
  memory_efficient_processing: true
```

## 🔐 Authentication Setup

### Default Admin User
```bash
# Create admin user
python -c "
from src.database.database import create_default_admin_user
import asyncio
asyncio.run(create_default_admin_user())
print('Admin user created: admin/admin123')
"
```

### Custom User Creation
```python
from src.database import crud, schemas
from src.auth import AuthService
import asyncio

async def create_user():
    auth_service = AuthService()

    user_data = schemas.UserCreate(
        username="therapist1",
        password="secure_password",
        is_admin=False
    )

    # Create user in database
    # Implementation depends on your database setup
    print(f"User created: {user_data.username}")

asyncio.run(create_user())
```

## 🧪 Testing & Validation

### Health Checks
```bash
# Basic health check
curl http://localhost:8001/health

# Detailed health check
curl http://localhost:8001/health/detailed

# AI model status
curl http://localhost:8001/ai/status
```

### API Testing
```bash
# Test authentication
curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Test document analysis (replace TOKEN with actual token)
curl -X POST "http://localhost:8001/analyze" \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@test_document.pdf" \
  -F "discipline=PT"
```

### Frontend Testing
```bash
# Test frontend connection
curl http://localhost:3000

# Check if Electron app loads
npm run electron:dev
```

## 🔄 Integration Patterns

### 1. Simple Integration
```python
import requests

class SimpleElectroAnalyzer:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def authenticate(self, username, password):
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        self.token = response.json()["access_token"]
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}"
        })

    def analyze_document(self, file_path, discipline="PT"):
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"discipline": discipline}
            response = self.session.post(
                f"{self.base_url}/analyze",
                files=files,
                data=data
            )
        return response.json()

# Usage
analyzer = SimpleElectroAnalyzer()
analyzer.authenticate("admin", "admin123")
result = analyzer.analyze_document("patient_note.pdf")
print(f"Task ID: {result['task_id']}")
```

### 2. Advanced Integration with Error Handling
```python
import requests
import time
from typing import Optional, Dict, Any

class AdvancedElectroAnalyzer:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.max_retries = 3
        self.retry_delay = 1

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate and store token."""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            self.token = data["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            return True

        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            return False

    def analyze_document(self, file_path: str, discipline: str = "PT") -> Optional[Dict[str, Any]]:
        """Analyze document with retry logic."""
        for attempt in range(self.max_retries):
            try:
                with open(file_path, "rb") as f:
                    files = {"file": f}
                    data = {"discipline": discipline}

                    response = self.session.post(
                        f"{self.base_url}/analyze",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    response.raise_for_status()
                    return response.json()

            except requests.exceptions.RequestException as e:
                print(f"Analysis attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    return None

    def wait_for_completion(self, task_id: str, timeout: int = 300) -> Optional[Dict[str, Any]]:
        """Wait for analysis completion."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = self.session.get(
                    f"{self.base_url}/analysis/{task_id}",
                    timeout=10
                )
                response.raise_for_status()

                data = response.json()
                if data["status"] == "completed":
                    return data
                elif data["status"] == "failed":
                    print(f"Analysis failed: {data.get('error', 'Unknown error')}")
                    return None

                time.sleep(2)  # Wait 2 seconds before next check

            except requests.exceptions.RequestException as e:
                print(f"Error checking status: {e}")
                time.sleep(5)

        print("Analysis timed out")
        return None

# Usage
analyzer = AdvancedElectroAnalyzer()
if analyzer.authenticate("admin", "admin123"):
    result = analyzer.analyze_document("patient_note.pdf", "PT")
    if result:
        final_result = analyzer.wait_for_completion(result["task_id"])
        if final_result:
            print(f"Compliance Score: {final_result['compliance_score']}")
```

### 3. Batch Processing Integration
```python
import asyncio
import aiohttp
from typing import List, Dict, Any

class BatchElectroAnalyzer:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.token: Optional[str] = None

    async def authenticate(self, username: str, password: str) -> bool:
        """Async authentication."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data["access_token"]
                    return True
                return False

    async def analyze_document(self, session: aiohttp.ClientSession, file_path: str, discipline: str = "PT") -> Dict[str, Any]:
        """Analyze single document."""
        headers = {"Authorization": f"Bearer {self.token}"}

        with open(file_path, "rb") as f:
            data = aiohttp.FormData()
            data.add_field("file", f, filename=file_path)
            data.add_field("discipline", discipline)

            async with session.post(
                f"{self.base_url}/analyze",
                data=data,
                headers=headers
            ) as response:
                return await response.json()

    async def analyze_batch(self, file_paths: List[str], discipline: str = "PT") -> List[Dict[str, Any]]:
        """Analyze multiple documents concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.analyze_document(session, file_path, discipline)
                for file_path in file_paths
            ]
            return await asyncio.gather(*tasks)

# Usage
async def main():
    analyzer = BatchElectroAnalyzer()
    if await analyzer.authenticate("admin", "admin123"):
        files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
        results = await analyzer.analyze_batch(files, "PT")

        for i, result in enumerate(results):
            print(f"Document {i+1}: Task ID {result['task_id']}")

asyncio.run(main())
```

## 🔧 Performance Optimization

### Connection Pooling
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_optimized_session():
    session = requests.Session()

    # Retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    # Connection pooling
    adapter = HTTPAdapter(
        pool_connections=10,
        pool_maxsize=20,
        max_retries=retry_strategy
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session
```

### Caching Strategy
```python
import functools
import time
from typing import Any, Callable

def cache_with_ttl(ttl_seconds: int = 300):
    """Cache function results with TTL."""
    def decorator(func: Callable) -> Callable:
        cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            now = time.time()

            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    return result

            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result

        return wrapper
    return decorator

# Usage
@cache_with_ttl(300)  # Cache for 5 minutes
def get_analysis_results(task_id: str) -> Dict[str, Any]:
    # Expensive API call
    pass
```

## 🚨 Error Handling Best Practices

### Comprehensive Error Handling
```python
import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ElectroAnalyzerError(Exception):
    """Base exception for ElectroAnalyzer errors."""
    pass

class AuthenticationError(ElectroAnalyzerError):
    """Authentication failed."""
    pass

class AnalysisError(ElectroAnalyzerError):
    """Analysis failed."""
    pass

class TimeoutError(ElectroAnalyzerError):
    """Operation timed out."""
    pass

def handle_api_response(response: requests.Response) -> Dict[str, Any]:
    """Handle API response with proper error handling."""
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            raise AuthenticationError("Invalid credentials")
        elif response.status_code == 429:
            raise ElectroAnalyzerError("Rate limit exceeded")
        elif response.status_code >= 500:
            raise ElectroAnalyzerError("Server error")
        else:
            raise ElectroAnalyzerError(f"HTTP error: {e}")
    except requests.exceptions.Timeout:
        raise TimeoutError("Request timed out")
    except requests.exceptions.ConnectionError:
        raise ElectroAnalyzerError("Connection failed")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise ElectroAnalyzerError(f"Unexpected error: {e}")
```

## 📊 Monitoring & Logging

### Application Monitoring
```python
import logging
import time
from functools import wraps

def monitor_performance(func):
    """Monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} completed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    return wrapper

# Usage
@monitor_performance
def analyze_document(file_path: str) -> Dict[str, Any]:
    # Analysis logic
    pass
```

### Health Monitoring
```python
import requests
import time
from typing import Dict, Any

class HealthMonitor:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url

    def check_health(self) -> Dict[str, Any]:
        """Check API health."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return {
                "status": "healthy",
                "response_time": response.elapsed.total_seconds(),
                "data": response.json()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def monitor_continuously(self, interval: int = 60):
        """Monitor health continuously."""
        while True:
            health = self.check_health()
            print(f"Health check: {health['status']}")

            if health["status"] == "unhealthy":
                logger.error(f"API is unhealthy: {health['error']}")

            time.sleep(interval)

# Usage
monitor = HealthMonitor()
health = monitor.check_health()
print(f"API Status: {health['status']}")
```

## 🔄 Deployment Strategies

### Development Deployment
```bash
# Start all services
./START_APP.bat  # Windows
# or
python start_robust.py
```

### Production Deployment
```bash
# Use production configuration
export ENVIRONMENT=production
export USE_AI_MOCKS=false
export SECRET_KEY=your-production-secret-key

# Start with production settings
python start_robust.py
```

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python", "start_robust.py"]
```

```bash
# Build and run
docker build -t electroanalyzer .
docker run -p 8001:8001 electroanalyzer
```

## 🧪 Testing Integration

### Unit Tests
```python
import pytest
import requests
from unittest.mock import Mock, patch

class TestElectroAnalyzerIntegration:
    def setup_method(self):
        self.base_url = "http://localhost:8001"
        self.client = requests.Session()

    def test_health_endpoint(self):
        response = self.client.get(f"{self.base_url}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_authentication(self):
        response = self.client.post(
            f"{self.base_url}/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    @patch('requests.post')
    def test_document_analysis(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"task_id": "test-123"}
        mock_response.status_code = 202
        mock_post.return_value = mock_response

        # Test analysis request
        response = self.client.post(
            f"{self.base_url}/analyze",
            files={"file": ("test.pdf", b"content")},
            data={"discipline": "PT"}
        )

        assert response.status_code == 202
        assert "task_id" in response.json()
```

### Integration Tests
```python
import pytest
import asyncio
from pathlib import Path

@pytest.mark.asyncio
async def test_complete_workflow():
    """Test complete document analysis workflow."""
    # 1. Authenticate
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8001/auth/login",
            json={"username": "admin", "password": "admin123"}
        ) as response:
            token = (await response.json())["access_token"]

    # 2. Upload document
    headers = {"Authorization": f"Bearer {token}"}
    test_file = Path("tests/test_data/sample_document.pdf")

    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field("file", test_file.open("rb"), filename="test.pdf")
        data.add_field("discipline", "PT")

        async with session.post(
            "http://localhost:8001/analyze",
            data=data,
            headers=headers
        ) as response:
            result = await response.json()
            task_id = result["task_id"]

    # 3. Wait for completion
    max_wait = 60  # 60 seconds
    wait_time = 0

    while wait_time < max_wait:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:8001/analysis/{task_id}",
                headers=headers
            ) as response:
                data = await response.json()

                if data["status"] == "completed":
                    assert "compliance_score" in data
                    assert "findings" in data
                    return
                elif data["status"] == "failed":
                    pytest.fail(f"Analysis failed: {data.get('error')}")

        await asyncio.sleep(2)
        wait_time += 2

    pytest.fail("Analysis timed out")
```

## 📞 Support & Troubleshooting

### Common Issues

#### 1. Authentication Failures
```bash
# Check if admin user exists
python -c "
from src.database.database import AsyncSessionLocal
from src.database.models import User
import asyncio

async def check_users():
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f'Found {len(users)} users')
        for user in users:
            print(f'  - {user.username} (admin: {user.is_admin})')

asyncio.run(check_users())
"
```

#### 2. Database Issues
```bash
# Check database connection
python -c "
from src.database.database import engine
import asyncio

async def test_db():
    try:
        async with engine.begin() as conn:
            await conn.execute('SELECT 1')
        print('Database connection successful')
    except Exception as e:
        print(f'Database connection failed: {e}')

asyncio.run(test_db())
"
```

#### 3. Performance Issues
```bash
# Check system resources
python -c "
import psutil
import os

process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
print(f'CPU usage: {process.cpu_percent():.1f}%')
"
```

### Getting Help

1. **Check Logs**: Review `logs/app.log` for errors
2. **Health Endpoints**: Use `/health` and `/health/detailed`
3. **Documentation**: Refer to API documentation
4. **Community**: Check GitHub issues and discussions

---

*This integration guide provides comprehensive instructions for integrating with the ElectroAnalyzer API. For additional support, please refer to the API documentation or contact the development team.*
