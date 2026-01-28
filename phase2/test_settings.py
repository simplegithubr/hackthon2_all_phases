"""Test settings loading"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    from src.db import settings, ENV_FILE
    print(f"ENV_FILE path: {ENV_FILE}")
    print(f"ENV_FILE exists: {ENV_FILE.exists()}")
    print(f"DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    print(f"JWT_SECRET: {settings.JWT_SECRET}")
    print(f"NEON_DATABASE_URL: {settings.NEON_DATABASE_URL[:50]}...")
    print(f"DEBUG: {settings.DEBUG}")
    print("\nAll settings loaded successfully!")
except Exception as e:
    print(f"Error loading settings: {e}")
    import traceback
    traceback.print_exc()
