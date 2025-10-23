"""Comprehensive test utilities and fixtures with proper async cleanup and global state management."""

import asyncio
import datetime
import logging
import os
import sys
import tempfile
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api.main import app
from src.core.vector_store import VectorStore, get_vector_store
from src.database import Base, get_async_db, models


# ============================================================================
# EVENT LOOP MANAGEMENT
# ============================================================================

@pytest.fixture(scope="session")
def event_loop_policy():
    """Set up event loop policy for the entire test session."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.get_event_loop_policy()


@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    """Create event loop for async tests with proper cleanup."""
    loop = event_loop_policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    # Properly shutdown the loop
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()
    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    loop.close()


# ============================================================================
# ASYNC FIXTURE CLEANUP (HIGHEST PRIORITY)
# ============================================================================

@pytest_asyncio.fixture(autouse=True)
async def cleanup_async_tasks():
    """Comprehensive async task cleanup with proper error handling."""
    yield

    # Get the current running loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return

    # Get current task to avoid cancelling ourselves
    current_task = asyncio.current_task(loop)
    
    # Cancel all pending tasks EXCEPT current task
    pending_tasks = [task for task in asyncio.all_tasks(loop) 
                     if task != current_task and not task.done()]
    
    for task in pending_tasks:
        if task:
            task.cancel()

    # Wait for all tasks to complete
    if pending_tasks:
        await asyncio.gather(*pending_tasks, return_exceptions=True)

    # Allow event loop to process cleanup
    await asyncio.sleep(0.001)


# ============================================================================
# MULTI-TIER CACHE CLEANUP (CRITICAL)
# ============================================================================

@pytest_asyncio.fixture(autouse=True)
async def cleanup_multi_tier_cache():
    """Cleanup MultiTierCacheSystem global state between tests."""
    yield

    try:
        from src.core.multi_tier_cache import multi_tier_cache

        # Shutdown cache system if it exists
        if multi_tier_cache is not None:
            await multi_tier_cache.shutdown()

        # Reset global instance
        import src.core.multi_tier_cache as cache_module
        cache_module.multi_tier_cache = None

    except Exception as e:
        logging.warning(f"Error cleaning up multi_tier_cache: {e}")


# ============================================================================
# SCHEDULER CLEANUP
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_scheduler():
    """Cleanup APScheduler between tests to prevent state pollution."""
    yield
    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        # Try to get the scheduler from main module
        try:
            from src.api.main import scheduler
            if scheduler and scheduler.running:
                scheduler.shutdown(wait=False)
        except (ImportError, AttributeError):
            pass

        # Reset scheduler in main module
        try:
            import src.api.main as main_module
            if hasattr(main_module, 'scheduler'):
                main_module.scheduler = BackgroundScheduler(daemon=True)
        except Exception:
            pass

    except Exception as e:
        logging.warning(f"Error cleaning up scheduler: {e}")


# ============================================================================
# GLOBAL STATE CLEANUP
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_global_state():
    """Cleanup global state and singletons between tests."""
    yield

    # Clear task registry
    try:
        from src.api.routers.analysis import tasks
        tasks.clear()
    except Exception:
        pass

    # Clear persistent task registry
    try:
        from src.core.persistent_task_registry import persistent_task_registry
        persistent_task_registry.tasks.clear()
    except Exception:
        pass

    # Reset vector store singleton
    try:
        from src.core.vector_store import VectorStore
        VectorStore._instance = None
    except Exception:
        pass

    # Reset hybrid retriever singleton
    try:
        from src.core.hybrid_retriever import HybridRetriever
        if hasattr(HybridRetriever, '_instance'):
            HybridRetriever._instance = None
    except Exception:
        pass

    # Reset retrieval service singleton
    try:
        from src.core.retrieval_service import RetriovalService
        if hasattr(RetriovalService, '_instance'):
            RetriovalService._instance = None
    except Exception:
        pass


# ============================================================================
# LOGGING CLEANUP (PROPER STREAM HANDLING)
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_logging():
    """Cleanup logging handlers and streams between tests with proper flush."""
    yield

    root_logger = logging.getLogger()

    # Properly close all handlers
    handlers_to_remove = []
    for handler in root_logger.handlers[:]:
        try:
            # Flush any buffered content
            if hasattr(handler, 'flush'):
                handler.flush()
            # Close the handler
            handler.close()
            handlers_to_remove.append(handler)
        except Exception as e:
            logging.warning(f"Error closing handler {handler}: {e}")
        finally:
            try:
                root_logger.removeHandler(handler)
            except Exception:
                pass

    # Ensure we don't have duplicate handlers
    for handler in handlers_to_remove:
        if handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    # Add a NullHandler to prevent "No handler found" warnings
    if not any(isinstance(h, logging.NullHandler) for h in root_logger.handlers):
        null_handler = logging.NullHandler()
        root_logger.addHandler(null_handler)

    # Reset logger level to default
    root_logger.setLevel(logging.WARNING)


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

async def _truncate_all(session: AsyncSession) -> None:
    """Truncate all tables to reset database state."""
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(table.delete())
    await session.commit()


def _reset_vector_store() -> VectorStore:
    """Reset vector store singleton and reinitialize."""
    VectorStore._instance = None  # type: ignore[attr-defined]
    store = VectorStore()
    store.initialize_index()
    return store


@pytest_asyncio.fixture(scope="session")
async def async_engine(tmp_path_factory: pytest.TempPathFactory):
    """Create async database engine for tests."""
    db_path = tmp_path_factory.mktemp("test_dbs") / "pytest.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="session")
def async_session_factory(async_engine):
    """Create async session factory for tests."""
    return async_sessionmaker(bind=async_engine, expire_on_commit=False, autoflush=False)


# ============================================================================
# HYBRID RETRIEVER FIXTURES (ASYNC MOCK)
# ============================================================================

@pytest_asyncio.fixture
async def mock_hybrid_retriever():
    """Create properly async-mocked HybridRetriever."""
    mock_retriever = AsyncMock()

    # Configure async method mocks
    mock_retriever.retrieve = AsyncMock(return_value=[
        {
            'id': '1',
            'content': 'Therapy documentation rule 1',
            'score': 0.95,
            'metadata': {'source': 'medicare_rules'}
        }
    ])

    mock_retriever.retrieve_by_tags = AsyncMock(return_value=[
        {
            'id': '1',
            'content': 'Tagged rule',
            'tags': ['compliance', 'documentation'],
            'score': 0.90
        }
    ])

    mock_retriever.batch_retrieve = AsyncMock(return_value={
        'query1': [{'id': '1', 'content': 'Result 1', 'score': 0.95}],
        'query2': [{'id': '2', 'content': 'Result 2', 'score': 0.87}]
    })

    return mock_retriever


@pytest_asyncio.fixture
async def patched_hybrid_retriever(mock_hybrid_retriever):
    """Patch HybridRetriever with async mock for all tests."""
    with patch('src.core.hybrid_retriever.HybridRetriever', return_value=mock_hybrid_retriever):
        with patch('src.core.analysis_service.HybridRetriever', return_value=mock_hybrid_retriever):
            yield mock_hybrid_retriever


# ============================================================================
# MULTI-TIER CACHE FIXTURES
# ============================================================================

@pytest_asyncio.fixture
async def multi_tier_cache_system():
    """Create isolated MultiTierCacheSystem instance for testing."""
    from src.core.multi_tier_cache import MultiTierCacheSystem

    cache = MultiTierCacheSystem(
        l1_size_mb=50,  # Smaller size for testing
        l2_enabled=False,
        l3_enabled=False,  # Disable file-based cache for tests
        default_ttl=300  # 5 minutes
    )

    yield cache

    # Proper shutdown
    try:
        await cache.shutdown()
    except Exception as e:
        logging.warning(f"Error shutting down cache: {e}")


# ============================================================================
# API CLIENT FIXTURES
# ============================================================================

@pytest_asyncio.fixture
async def async_client():
    """Create async HTTP client for API testing."""
    async with AsyncClient(
        app=app,
        base_url="http://test",
        transport=ASGITransport(app=app)
    ) as client:
        yield client


@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing."""
    with patch('src.core.analysis_service.AnalysisService') as mock_service:
        mock_instance = Mock()
        mock_instance.use_mocks = True
        mock_instance.analyze_document.return_value = {
            "compliance_score": 85.5,
            "findings": [
                {
                    "rule_id": "test_rule",
                    "risk": "Medium",
                    "message": "Test finding",
                    "confidence": 0.8
                }
            ]
        }
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_document():
    """Create sample document for testing."""
    content = """
    Patient Progress Note

    Patient: John Doe
    Date: 2024-01-01

    Assessment:
    Patient presents with improved mobility and strength.
    Treatment goals are being met.

    Plan:
    Continue current treatment plan.
    Reassess in 2 weeks.
    """

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def sample_pdf():
    """Create sample PDF for testing."""
    # This would create a minimal PDF file
    # For now, we'll use a text file with PDF extension
    content = b"PDF content placeholder"

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def mock_file_upload():
    """Mock file upload for testing."""
    return {
        "file": ("test.txt", "test content", "text/plain"),
        "document_name": "Test Document",
        "rubric": "pt_compliance_rubric"
    }


@pytest.fixture
def performance_test_data():
    """Create performance test data."""
    return {
        "requests": [
            {"method": "GET", "url": "/health/", "expected_time": 0.1},
            {"method": "POST", "url": "/analysis/start", "expected_time": 0.5},
            {"method": "GET", "url": "/metrics", "expected_time": 0.2}
        ],
        "concurrent_users": 10,
        "duration_seconds": 30
    }


@pytest.fixture
def security_test_payloads():
    """Security test payloads."""
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ],
        "xss": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts"
        ],
        "command_injection": [
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& whoami"
        ]
    }


@pytest.fixture
def mock_metrics_collector():
    """Mock metrics collector for testing."""
    with patch('src.core.performance_metrics_collector.metrics_collector') as mock_collector:
        mock_collector.get_metrics_summary.return_value = {
            "uptime_seconds": 3600,
            "requests": {
                "total": 100,
                "avg_duration_ms": 150.5,
                "error_count": 5,
                "error_rate_percent": 5.0
            },
            "system": {
                "memory_usage_mb": 512.0,
                "cpu_usage_percent": 25.5
            }
        }
        yield mock_collector


@pytest.fixture
def mock_health_checker():
    """Mock health checker for testing."""
    with patch('src.api.routers.health_advanced.health_checker') as mock_checker:
        mock_checker.get_overall_health.return_value = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "uptime_seconds": 3600,
            "checks": {
                "database": {"status": "healthy"},
                "ai_models": {"status": "healthy"},
                "system_resources": {"status": "healthy"}
            }
        }
        yield mock_checker


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "use_ai_mocks": True,
        "database_url": "sqlite:///:memory:",
        "log_level": "DEBUG",
        "max_request_size": 1024,
        "rate_limit": "100/minute"
    }


@pytest.fixture
def mock_environment():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        "SECRET_KEY": "test-secret-key",
        "ENVIRONMENT": "testing",
        "USE_AI_MOCKS": "true",
        "LOG_LEVEL": "DEBUG"
    }):
        yield


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection for testing."""
    mock_ws = Mock()
    mock_ws.accept = Mock()
    mock_ws.send_json = Mock()
    mock_ws.receive_text = Mock()
    mock_ws.close = Mock()
    return mock_ws


@pytest.fixture
def mock_task_manager():
    """Mock task manager for testing."""
    with patch('src.api.routers.analysis.tasks', {}) as mock_tasks:
        yield mock_tasks


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    with patch('src.core.vector_store.get_vector_store') as mock_store:
        mock_instance = Mock()
        mock_instance.is_initialized = True
        mock_instance.add_vectors = Mock()
        mock_store.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    with patch('src.core.llm_service.LLMService') as mock_service:
        mock_instance = Mock()
        mock_instance.is_ready.return_value = True
        mock_instance.generate.return_value = "Mock response"
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_retriever():
    """Mock retriever for testing."""
    with patch('src.core.hybrid_retriever.HybridRetriever') as mock_retriever:
        mock_instance = Mock()
        mock_instance.initialize = Mock()
        mock_instance.retrieve.return_value = [
            {"text": "Mock retrieved text", "score": 0.9}
        ]
        mock_retriever.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_ner_service():
    """Mock NER service for testing."""
    with patch('src.core.ner.ClinicalNERService') as mock_service:
        mock_instance = Mock()
        mock_instance.extract_entities.return_value = [
            {"text": "Patient", "label": "PERSON", "confidence": 0.9}
        ]
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "username": "testuser",
        "password": "testpassword",
        "is_active": True,
        "is_admin": False
    }


@pytest.fixture
def test_analysis_data():
    """Test analysis data."""
    return {
        "document_name": "Test Document",
        "rubric": "pt_compliance_rubric",
        "strictness": "standard",
        "discipline": "pt"
    }


@pytest.fixture
def test_report_data():
    """Test report data."""
    return {
        "id": 1,
        "document_name": "Test Document",
        "compliance_score": 85.5,
        "analysis_date": "2024-01-01T00:00:00Z",
        "findings": [
            {
                "rule_id": "test_rule",
                "risk": "Medium",
                "message": "Test finding",
                "confidence": 0.8
            }
        ]
    }


# Test markers
pytestmark = [
    pytest.mark.asyncio,
]


# ============================================================================
# DATABASE STATE MANAGEMENT (CRITICAL FOR TEST ISOLATION)
# ============================================================================

@pytest_asyncio.fixture(autouse=True)
async def cleanup_database_state(async_session_factory=None):
    """Cleanup and reset database state between tests."""
    # Skip if no session factory available
    if not async_session_factory:
        yield
        return
    
    # Pre-test: Truncate all tables to ensure clean state
    try:
        async with async_session_factory() as session:
            try:
                # Disable foreign key constraints temporarily
                if 'sqlite' in str(async_session_factory.kw.get('bind', '')):
                    await asyncio.wait_for(session.execute(text('PRAGMA foreign_keys = OFF')), timeout=5.0)
                
                # Delete all data from all tables in reverse order (for FK constraints)
                for table in reversed(Base.metadata.sorted_tables):
                    try:
                        await asyncio.wait_for(session.execute(table.delete()), timeout=5.0)
                    except Exception:
                        pass
                
                await asyncio.wait_for(session.commit(), timeout=5.0)
                
                # Re-enable foreign key constraints
                if 'sqlite' in str(async_session_factory.kw.get('bind', '')):
                    await asyncio.wait_for(session.execute(text('PRAGMA foreign_keys = ON')), timeout=5.0)
            except Exception as e:
                logging.debug(f"Error pre-cleaning database: {e}")
                try:
                    await session.rollback()
                except Exception:
                    pass
    except Exception as e:
        logging.warning(f"Error pre-cleaning database: {e}")
    
    yield
    
    # Post-test: Cleanup after test
    if not async_session_factory:
        return
        
    try:
        async with async_session_factory() as session:
            try:
                # Disable foreign keys
                if 'sqlite' in str(async_session_factory.kw.get('bind', '')):
                    await asyncio.wait_for(session.execute(text('PRAGMA foreign_keys = OFF')), timeout=5.0)
                
                # Truncate all tables
                for table in reversed(Base.metadata.sorted_tables):
                    try:
                        await asyncio.wait_for(session.execute(table.delete()), timeout=5.0)
                    except Exception as e:
                        logging.debug(f"Error deleting from {table.name}: {e}")
                
                await asyncio.wait_for(session.commit(), timeout=5.0)
                
                # Re-enable foreign keys
                if 'sqlite' in str(async_session_factory.kw.get('bind', '')):
                    await asyncio.wait_for(session.execute(text('PRAGMA foreign_keys = ON')), timeout=5.0)
            except Exception as e:
                logging.debug(f"Error post-cleaning database: {e}")
                try:
                    await session.rollback()
                except Exception:
                    pass
    except Exception as e:
        logging.warning(f"Error post-cleaning database: {e}")


@pytest_asyncio.fixture
async def db_session(async_session_factory):
    """Provide a clean database session for each test."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture
async def populated_test_db(db_session: AsyncSession):
    """Create a populated test database with sample data."""
    # Create test users
    test_user = models.User(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$test_hash",
        is_active=True
    )
    db_session.add(test_user)

    # Flush to get IDs
    await db_session.flush()

    # Create test analysis reports
    now = datetime.datetime.now(datetime.timezone.utc)
    test_report = models.AnalysisReport(
        document_name="test_document.pdf",
        compliance_score=85.5,
        document_type="Progress Note",
        discipline="PT",
        analysis_date=now,
        analysis_result={
            "discipline": "PT",
            "document_type": "Progress Note",
            "summary": "Test analysis summary"
        }
    )
    db_session.add(test_report)

    await db_session.commit()

    return db_session


# ============================================================================
# MOCK STATE MANAGEMENT (PREVENT MOCK POLLUTION)
# ============================================================================

@pytest.fixture(autouse=True)
def reset_mock_state():
    """Reset all mock patches and state between tests."""
    yield

    # Clear all patch objects
    from unittest.mock import patch
    patch.stopall()

    # Reset common mock singletons
    mock_singletons = [
        'src.core.analysis_service._instance',
        'src.core.compliance_analyzer._instance',
        'src.core.llm_service._instance',
    ]

    for singleton_path in mock_singletons:
        try:
            module_path, attr = singleton_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[attr.split('_')[0]])
            if hasattr(module, attr.split('_')[0]):
                cls = getattr(module, attr.split('_')[0])
                if hasattr(cls, attr):
                    setattr(cls, attr, None)
        except Exception as e:
            logging.debug(f"Error resetting mock singleton {singleton_path}: {e}")


@pytest.fixture
def mock_cleanup_context():
    """Provide a context manager for managing mocks in tests."""
    active_patches = []
    active_mocks = {}

    def patch_obj(target, **kwargs):
        """Patch an object and track it for cleanup."""
        patcher = patch(target, **kwargs)
        mock_obj = patcher.start()
        active_patches.append(patcher)
        active_mocks[target] = mock_obj
        return mock_obj

    def reset():
        """Reset all active patches."""
        for patcher in active_patches:
            try:
                patcher.stop()
            except Exception:
                pass
        active_patches.clear()
        active_mocks.clear()

    yield {
        'patch': patch_obj,
        'mocks': active_mocks,
        'reset': reset
    }

    # Cleanup
    reset()


# ============================================================================
# GLOBAL REGISTRY STATE MANAGEMENT
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_registries():
    """Cleanup all global registries and state holders between tests."""
    yield

    # Reset task registries
    registries_to_clear = [
        ('src.api.routers.analysis', 'tasks'),
        ('src.core.persistent_task_registry', 'persistent_task_registry', 'tasks'),
        ('src.core.service_manager', 'service_manager', '_services'),
        ('src.core.plugin_system', 'plugin_registry', '_plugins'),
    ]

    for registry_info in registries_to_clear:
        try:
            if len(registry_info) == 2:
                module_name, attr_name = registry_info
                module = __import__(module_name, fromlist=[attr_name])
                obj = getattr(module, attr_name, None)
                if isinstance(obj, dict):
                    obj.clear()
            else:
                module_name, obj_name, attr_name = registry_info
                module = __import__(module_name, fromlist=[obj_name])
                obj = getattr(module, obj_name, None)
                if hasattr(obj, attr_name):
                    attr = getattr(obj, attr_name)
                    if isinstance(attr, dict):
                        attr.clear()
        except Exception as e:
            logging.debug(f"Error clearing registry {registry_info}: {e}")


@pytest.fixture(autouse=True)
def cleanup_model_state():
    """Cleanup model-level state and class variables between tests."""
    yield

    # Reset model class state variables
    model_classes_with_state = [
        ('src.database.models', 'User', '_cache'),
        ('src.database.models', 'AnalysisReport', '_cache'),
        ('src.core.compliance_analyzer', 'ComplianceAnalyzer', '_rule_cache'),
    ]

    for module_name, class_name, state_attr in model_classes_with_state:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name, None)
            if cls and hasattr(cls, state_attr):
                state = getattr(cls, state_attr)
                if isinstance(state, dict):
                    state.clear()
                elif isinstance(state, list):
                    state.clear()
        except Exception as e:
            logging.debug(f"Error resetting model state {class_name}.{state_attr}: {e}")


# ============================================================================
# COMPREHENSIVE STATE RESET UTILITY
# ============================================================================

class GlobalStateManager:
    """Manage and reset all global state in the application."""

    @staticmethod
    async def reset_all():
        """Reset all global state comprehensively."""
        await GlobalStateManager.reset_async_state()
        await GlobalStateManager.reset_cache_state()
        GlobalStateManager.reset_singletons()
        GlobalStateManager.reset_registries()
        GlobalStateManager.reset_model_state()

    @staticmethod
    async def reset_async_state():
        """Reset async task state."""
        try:
            loop = asyncio.get_running_loop()
            pending = asyncio.all_tasks(loop)
            for task in pending:
                if not task.done():
                    task.cancel()
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)
        except RuntimeError:
            pass

    @staticmethod
    async def reset_cache_state():
        """Reset cache systems."""
        try:
            from src.core.multi_tier_cache import multi_tier_cache
            if multi_tier_cache:
                await multi_tier_cache.shutdown()
                import src.core.multi_tier_cache as cache_module
                cache_module.multi_tier_cache = None
        except Exception as e:
            logging.debug(f"Cache reset error: {e}")

    @staticmethod
    def reset_singletons():
        """Reset all singleton instances."""
        singletons = [
            ('src.core.vector_store', 'VectorStore'),
            ('src.core.hybrid_retriever', 'HybridRetriever'),
            ('src.core.analysis_service', 'AnalysisService'),
            ('src.core.compliance_analyzer', 'ComplianceAnalyzer'),
        ]

        for module_name, class_name in singletons:
            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                if hasattr(cls, '_instance'):
                    cls._instance = None
            except Exception as e:
                logging.debug(f"Singleton reset error for {class_name}: {e}")

    @staticmethod
    def reset_registries():
        """Reset all global registries."""
        registries = [
            ('src.api.routers.analysis', 'tasks'),
            ('src.core.persistent_task_registry', 'persistent_task_registry'),
        ]

        for module_name, obj_name in registries:
            try:
                module = __import__(module_name, fromlist=[obj_name])
                obj = getattr(module, obj_name)
                if hasattr(obj, 'clear'):
                    obj.clear()
                elif isinstance(obj, dict):
                    obj.clear()
                elif hasattr(obj, 'tasks') and isinstance(obj.tasks, dict):
                    obj.tasks.clear()
            except Exception as e:
                logging.debug(f"Registry reset error for {obj_name}: {e}")

    @staticmethod
    def reset_model_state():
        """Reset model-level state."""
        # This is handled by cleanup_model_state fixture
        pass


@pytest_asyncio.fixture
async def global_state_manager():
    """Provide access to global state manager."""
    yield GlobalStateManager
    # Comprehensive cleanup at end
    await GlobalStateManager.reset_all()


# ============================================================================
# SYSTEM DEPENDENCY MOCKING (HANDLE MISSING SYSTEM LIBRARIES)
# ============================================================================

@pytest.fixture(autouse=True)
def mock_system_dependencies():
    """Mock system dependencies that may not be available on all platforms."""
    
    # Mock WeasyPrint/Cairo/GTK if not available or broken
    try:
        import weasyprint
        logging.debug("WeasyPrint imported successfully")
    except (ImportError, OSError) as e:
        logging.debug(f"WeasyPrint import failed ({type(e).__name__}), creating mock")
        weasyprint_mock = Mock()
        weasyprint_mock.HTML = Mock(return_value=Mock(write_pdf=Mock(return_value=b"PDF")))
        sys.modules['weasyprint'] = weasyprint_mock
    
    # Mock cairo if not available
    try:
        import cairo
    except (ImportError, OSError):
        logging.debug("Cairo not available, creating mock")
        cairo_mock = Mock()
        sys.modules['cairo'] = cairo_mock
    
    # Mock gi (GTK) if not available
    try:
        import gi
    except (ImportError, OSError):
        logging.debug("gi (GTK) not available, creating mock")
        gi_mock = Mock()
        gi_mock.require_version = Mock()
        gi_mock.Repository = Mock()
        sys.modules['gi'] = gi_mock
        sys.modules['gi.repository'] = Mock()
        sys.modules['gi.repository.Gtk'] = Mock()
    
    yield
    
    # Cleanup mocks
    for module_name in ['weasyprint', 'cairo', 'gi', 'gi.repository', 'gi.repository.Gtk']:
        if module_name in sys.modules:
            try:
                # Only remove if it's a mock we added
                mod = sys.modules[module_name]
                if isinstance(mod, Mock):
                    del sys.modules[module_name]
            except Exception:
                pass


# ============================================================================
# RESOURCE CONSTRAINT HANDLING
# ============================================================================

@pytest.fixture
def mock_system_memory():
    """Mock system memory pressure for testing cache behavior."""

    class MemoryMocker:
        """Mock and control memory availability in tests."""

        def __init__(self):
            self.original_virtual_memory = None
            self.memory_available = None

        def set_low_memory(self, available_mb: int = 100):
            """Simulate low memory condition."""
            import psutil

            self.original_virtual_memory = psutil.virtual_memory

            def mock_virtual_memory():
                from unittest.mock import Mock
                vm = Mock()
                vm.available = available_mb * 1024 * 1024  # Convert to bytes
                vm.total = 1024 * 1024 * 1024  # 1GB total
                vm.used = vm.total - vm.available
                vm.percent = (vm.used / vm.total) * 100
                return vm

            psutil.virtual_memory = mock_virtual_memory

        def set_normal_memory(self, available_gb: int = 8):
            """Reset to normal memory condition."""
            import psutil

            if self.original_virtual_memory:
                psutil.virtual_memory = self.original_virtual_memory
            else:
                # Create realistic memory mock
                def mock_virtual_memory():
                    from unittest.mock import Mock
                    vm = Mock()
                    vm.available = available_gb * 1024 * 1024 * 1024
                    vm.total = available_gb * 1024 * 1024 * 1024
                    vm.used = 0
                    vm.percent = 0
                    return vm

                psutil.virtual_memory = mock_virtual_memory

        def restore(self):
            """Restore original memory function."""
            if self.original_virtual_memory:
                import psutil
                psutil.virtual_memory = self.original_virtual_memory

    mocker = MemoryMocker()
    mocker.set_normal_memory()

    yield mocker

    mocker.restore()


@pytest.fixture
def mock_disk_space():
    """Mock disk space availability for testing cache disk tier."""

    class DiskSpaceMocker:
        """Mock and control disk space availability in tests."""

        def __init__(self):
            self.original_disk_usage = None

        def set_low_disk(self, free_mb: int = 50):
            """Simulate low disk space condition."""
            import psutil
            from unittest.mock import Mock

            self.original_disk_usage = psutil.disk_usage

            def mock_disk_usage(path):
                usage = Mock()
                usage.total = 1024 * 1024 * 1024  # 1GB
                usage.used = usage.total - (free_mb * 1024 * 1024)
                usage.free = free_mb * 1024 * 1024
                usage.percent = (usage.used / usage.total) * 100
                return usage

            psutil.disk_usage = mock_disk_usage

        def set_high_disk(self, free_gb: int = 100):
            """Reset to high disk space condition."""
            import psutil
            from unittest.mock import Mock

            if self.original_disk_usage:
                psutil.disk_usage = self.original_disk_usage
            else:
                def mock_disk_usage(path):
                    usage = Mock()
                    usage.total = free_gb * 1024 * 1024 * 1024
                    usage.used = 0
                    usage.free = free_gb * 1024 * 1024 * 1024
                    usage.percent = 0
                    return usage

                psutil.disk_usage = mock_disk_usage

        def restore(self):
            """Restore original disk usage function."""
            if self.original_disk_usage:
                import psutil
                psutil.disk_usage = self.original_disk_usage

    mocker = DiskSpaceMocker()
    mocker.set_high_disk()

    yield mocker

    mocker.restore()


@pytest.fixture
def mock_cpu_load():
    """Mock CPU load for testing performance under pressure."""

    class CPULoadMocker:
        """Mock and control CPU load in tests."""

        def __init__(self):
            self.original_cpu_percent = None
            self.original_cpu_count = None

        def set_high_load(self, cpu_percent: float = 90.0):
            """Simulate high CPU load."""
            import psutil

            self.original_cpu_percent = psutil.cpu_percent
            self.original_cpu_count = psutil.cpu_count

            psutil.cpu_percent = Mock(return_value=cpu_percent)
            psutil.cpu_count = Mock(return_value=4)

        def set_normal_load(self, cpu_percent: float = 25.0):
            """Reset to normal CPU load."""
            import psutil

            if self.original_cpu_percent:
                psutil.cpu_percent = self.original_cpu_percent
            else:
                psutil.cpu_percent = Mock(return_value=cpu_percent)

            if self.original_cpu_count:
                psutil.cpu_count = self.original_cpu_count

        def restore(self):
            """Restore original CPU functions."""
            if self.original_cpu_percent:
                import psutil
                psutil.cpu_percent = self.original_cpu_percent
            if self.original_cpu_count:
                import psutil
                psutil.cpu_count = self.original_cpu_count

    mocker = CPULoadMocker()
    mocker.set_normal_load()

    yield mocker

    mocker.restore()


# ============================================================================
# PDF EXPORT TEST HELPERS
# ============================================================================

@pytest.fixture
def mock_weasyprint_pdf_export():
    """Mock WeasyPrint PDF export for testing without system dependencies."""

    class WeasyPrintMocker:
        """Mock WeasyPrint PDF export."""

        def __init__(self):
            self.export_called = False
            self.last_html_content = None

        def generate_pdf(self, html_content: str) -> bytes:
            """Generate mock PDF from HTML content."""
            self.export_called = True
            self.last_html_content = html_content

            # Return realistic PDF header
            return b"%PDF-1.4\n%Mock PDF generated by test\n" + b"test_content"

        def verify_export_called(self):
            """Verify that export was called."""
            return self.export_called

        def reset(self):
            """Reset state for next test."""
            self.export_called = False
            self.last_html_content = None

    mocker = WeasyPrintMocker()

    # Patch PDF export
    with patch('src.core.pdf_export_service.PDFExportService.generate_pdf',
               side_effect=mocker.generate_pdf):
        yield mocker


@pytest.fixture
def mock_pdf_export_service():
    """Mock the entire PDF export service."""
    from unittest.mock import AsyncMock, Mock

    mock_service = AsyncMock()
    mock_service.generate_pdf = AsyncMock(return_value=b"%PDF-1.4\nMock PDF")
    mock_service.export_to_file = AsyncMock()
    mock_service.export_to_buffer = AsyncMock(return_value=b"%PDF-1.4\nMock PDF")

    with patch('src.core.pdf_export_service.PDFExportService', return_value=mock_service):
        yield mock_service


# ============================================================================
# RESOURCE-DEPENDENT TEST HELPERS
# ============================================================================

@pytest.fixture
def skip_if_resource_unavailable():
    """Skip test if required system resources are not available."""

    def check_resource(resource_name: str, min_available: int = None) -> bool:
        """Check if a resource is available."""
        import psutil

        if resource_name == "memory":
            available_mb = psutil.virtual_memory().available / (1024 * 1024)
            required_mb = min_available or 500
            if available_mb < required_mb:
                pytest.skip(f"Insufficient memory: {available_mb}MB < {required_mb}MB required")
            return True

        elif resource_name == "disk":
            free_mb = psutil.disk_usage('/').free / (1024 * 1024)
            required_mb = min_available or 1000
            if free_mb < required_mb:
                pytest.skip(f"Insufficient disk space: {free_mb}MB < {required_mb}MB required")
            return True

        elif resource_name == "cpu":
            cpu_percent = psutil.cpu_percent(interval=0.1)
            max_percent = min_available or 80
            if cpu_percent > max_percent:
                pytest.skip(f"High CPU load: {cpu_percent}% > {max_percent}% threshold")
            return True

        return True

    return check_resource


@pytest.fixture
def resource_aware_test_context():
    """Provide context-aware resource testing."""

    class ResourceContext:
        """Manage resource-dependent test execution."""

        def __init__(self):
            import psutil
            self.psutil = psutil
            self.initial_memory = None
            self.initial_disk = None
            self.initial_cpu = None

        def capture_initial_state(self):
            """Capture initial resource state."""
            self.initial_memory = self.psutil.virtual_memory()
            self.initial_disk = self.psutil.disk_usage('/')
            self.initial_cpu = self.psutil.cpu_percent(interval=0.1)

            return {
                'memory_available_mb': self.initial_memory.available / (1024 * 1024),
                'disk_free_mb': self.initial_disk.free / (1024 * 1024),
                'cpu_percent': self.initial_cpu
            }

        def assert_resources_stable(self, max_memory_delta_mb: float = 100,
                                    max_cpu_delta: float = 10):
            """Assert that resources remained stable during test."""
            current_memory = self.psutil.virtual_memory()
            current_cpu = self.psutil.cpu_percent(interval=0.1)

            memory_delta_mb = (self.initial_memory.available - current_memory.available) / (1024 * 1024)
            cpu_delta = abs(current_cpu - self.initial_cpu)

            assert memory_delta_mb < max_memory_delta_mb, \
                f"Memory usage increased by {memory_delta_mb}MB (max {max_memory_delta_mb}MB)"
            assert cpu_delta < max_cpu_delta, \
                f"CPU usage changed by {cpu_delta}% (max {max_cpu_delta}%)"

        def get_available_memory_mb(self) -> float:
            """Get current available memory in MB."""
            return self.psutil.virtual_memory().available / (1024 * 1024)

        def get_available_disk_mb(self) -> float:
            """Get current available disk space in MB."""
            return self.psutil.disk_usage('/').free / (1024 * 1024)

        def get_cpu_percent(self) -> float:
            """Get current CPU percentage."""
            return self.psutil.cpu_percent(interval=0.1)

    context = ResourceContext()
    context.capture_initial_state()

    yield context


# ============================================================================
# CACHE MEMORY PRESSURE TESTING
# ============================================================================

@pytest.fixture
async def cache_under_memory_pressure(mock_system_memory, multi_tier_cache_system):
    """Provide cache system under simulated memory pressure."""

    # Simulate memory pressure
    mock_system_memory.set_low_memory(available_mb=100)

    yield multi_tier_cache_system

    # Restore normal memory
    mock_system_memory.set_normal_memory()


@pytest.fixture
async def cache_with_full_disk(mock_disk_space, multi_tier_cache_system):
    """Provide cache system with low disk space."""

    # Simulate disk pressure
    mock_disk_space.set_low_disk(free_mb=50)

    yield multi_tier_cache_system

    # Restore normal disk
    mock_disk_space.set_high_disk()


# ============================================================================
# SKIP DECORATORS FOR SYSTEM DEPENDENCIES
# ============================================================================

def skip_without_weasyprint(func):
    """Skip test if WeasyPrint is not available."""
    try:
        import weasyprint
        return func
    except ImportError:
        return pytest.mark.skip(reason="WeasyPrint not available")(func)


def skip_without_system_resource(resource_name: str, min_required: int = None):
    """Skip test if required system resource is not available."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import psutil

            if resource_name == "memory":
                available_mb = psutil.virtual_memory().available / (1024 * 1024)
                required_mb = min_required or 500
                if available_mb < required_mb:
                    pytest.skip(f"Insufficient {resource_name}: {available_mb}MB < {required_mb}MB")

            elif resource_name == "disk":
                free_mb = psutil.disk_usage('/').free / (1024 * 1024)
                required_mb = min_required or 1000
                if free_mb < required_mb:
                    pytest.skip(f"Insufficient {resource_name}: {free_mb}MB < {required_mb}MB")

            return func(*args, **kwargs)
        return wrapper
    return decorator