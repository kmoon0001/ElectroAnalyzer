import warnings
warnings.simplefilter('ignore')
from src.core.advanced_security_system import security_system
from src.auth import get_auth_service

auth = get_auth_service()
token = security_system.generate_secure_token(user_id=123, expires_in_hours=1)
print('TOKEN_PREFIX', token[:20])
payload = security_system.validate_token(token)
print('PAYLOAD_USER', payload.get('user_id') if payload else None)
print('ALG', auth.algorithm)
