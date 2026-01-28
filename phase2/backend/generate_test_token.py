"""Generate a test JWT token for API testing"""
import os
import sys
from datetime import datetime, timedelta

# Try importing jose first (used by your FastAPI app)
try:
    from jose import jwt
    print("Using python-jose library")
except ImportError:
    print("Error: python-jose not installed. Install with: pip install python-jose[cryptography]")
    sys.exit(1)

from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv(".env")

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET not found in .env")

# Create test token with user_id in 'sub' claim
payload = {
    "sub": "test-user-123",  # user_id
    "exp": datetime.utcnow() + timedelta(days=1),  # Expires in 1 day
    "iat": datetime.utcnow(),  # Issued at
}

token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
print(f"\nTest JWT Token:\n{token}")
print(f"\nUse this token in your curl requests:")
print(f'curl -H "Authorization: Bearer {token}" http://127.0.0.1:8000/api/tasks')
