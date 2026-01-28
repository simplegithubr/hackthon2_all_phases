#!/usr/bin/env python3
"""Quick JWT token generator for testing"""
from datetime import datetime, timedelta
import base64
import hmac
import hashlib
import json

JWT_SECRET = "a-string-secret-at-least-256-bits-long"

# Header
header = {"alg": "HS256", "typ": "JWT"}
header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")

# Payload
payload = {
    "sub": "test-user-123",
    "exp": int((datetime.utcnow() + timedelta(days=1)).timestamp()),
    "iat": int(datetime.utcnow().timestamp())
}
payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

# Signature
message = f"{header_b64}.{payload_b64}"
signature = hmac.new(
    JWT_SECRET.encode(),
    message.encode(),
    hashlib.sha256
).digest()
signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

# Final token
token = f"{header_b64}.{payload_b64}.{signature_b64}"
print(f"JWT Token: {token}")
