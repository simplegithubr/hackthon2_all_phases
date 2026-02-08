import os

key = os.getenv("OPENROUTER_API_KEY")
print("OPENROUTER_API_KEY:", key if key else "Not found")
