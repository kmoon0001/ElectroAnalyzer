"""Logging utilities for safe logging with extra fields."""

# Reserved LogRecord fields that cannot be used as extra fields
RESERVED_LOGRECORD_FIELDS = {
    'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname',
    'levelno', 'lineno', 'module', 'msecs', 'millisecs', 'message', 'pathname',
    'process', 'processName', 'relativeCreated', 'thread', 'threadName', 'exc_info',
    'exc_text', 'stack_info', 'taskName'
}


def filter_reserved_fields(data: dict) -> dict:
    """
    Filter out reserved LogRecord fields from a dictionary.
    
    Args:
        data: Dictionary potentially containing reserved field names
        
    Returns:
        Dictionary with reserved fields removed
    """
    return {k: v for k, v in data.items() if k not in RESERVED_LOGRECORD_FIELDS}
