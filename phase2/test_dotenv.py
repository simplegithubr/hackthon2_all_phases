"""Test dotenv loading"""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / ".env"

print(f"ENV_FILE: {ENV_FILE}")
print(f"EXISTS: {ENV_FILE.exists()}")
print(f"ABSOLUTE: {ENV_FILE.absolute()}")

# Load it
result = load_dotenv(ENV_FILE)
print(f"\nload_dotenv result: {result}")

# Check what we got
print(f"\nJWT_SECRET from os.getenv: {os.getenv('JWT_SECRET')}")
print(f"DATABASE_URL from os.getenv: {os.getenv('DATABASE_URL')[:50] if os.getenv('DATABASE_URL') else None}...")
