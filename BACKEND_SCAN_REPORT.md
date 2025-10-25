# Backend Security and Quality Scan Report

## Summary
- Critical Issues: 0
- High Severity: 9
- Medium Severity: 1
- Low Severity: 0
- Warnings: 78

## High Severity Issues
- **src\core\async_file_handler.py:107** - Blocking call in async function: open\([^)]*\)
- **src\core\async_file_handler.py:146** - Blocking call in async function: open\([^)]*\)
- **src\core\human_feedback_system.py:658** - Blocking call in async function: open\([^)]*\)
- **src\core\ml_scheduler.py:219** - Blocking call in async function: open\([^)]*\)
- **src\core\pdf_export_service_fallback_clean.py:193** - Blocking call in async function: open\([^)]*\)
- **src\core\shared_utils.py:199** - Blocking call in async function: open\([^)]*\)
- **src\api\routers\admin.py:58** - Blocking call in async function: open\([^)]*\)
- **src\api\routers\admin.py:68** - Blocking call in async function: open\([^)]*\)
- **src\api\routers\health_advanced.py:161** - Blocking call in async function: requests\.(get|post|put|delete|patch)\(

## Medium Severity Issues (showing first 10)
- **src\core\advanced_performance_optimizer.py:69** - Bare except clause - should specify exception type

