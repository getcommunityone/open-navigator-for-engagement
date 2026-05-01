#!/usr/bin/env python3
"""Test the OAuth flow end-to-end"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("🔐 OAuth Configuration Test")
print("=" * 60)

# Check environment variables
checks = {
    'HUGGINGFACE_CLIENT_ID': os.getenv('HUGGINGFACE_CLIENT_ID'),
    'HUGGINGFACE_CLIENT_SECRET': os.getenv('HUGGINGFACE_CLIENT_SECRET'),
    'FRONTEND_URL': os.getenv('FRONTEND_URL'),
    'API_BASE_URL': os.getenv('API_BASE_URL'),
    'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
    'DATABASE_URL': os.getenv('DATABASE_URL'),
}

all_good = True
for key, value in checks.items():
    if value:
        preview = value[:30] + '...' if len(value) > 30 else value
        print(f"✅ {key:30} = {preview}")
    else:
        print(f"❌ {key:30} = MISSING")
        all_good = False

print("=" * 60)

if all_good:
    print("✅ All OAuth environment variables are configured!")
    print("\n📝 Next steps:")
    print("1. Make sure API server is running")
    print("2. Open http://localhost:5173 in incognito")
    print("3. Open browser console (F12)")
    print("4. Click Login → HuggingFace")
    print("5. Watch console for logs")
else:
    print("❌ Some environment variables are missing!")
    print("\nPlease check your .env file.")
    sys.exit(1)

# Test database connection
print("\n" + "=" * 60)
print("💾 Database Test")
print("=" * 60)

try:
    from api.database import init_db
    from api.models import User
    
    init_db()
    print("✅ Database initialized successfully")
    
    # Try to query users
    from api.database import SessionLocal
    db = SessionLocal()
    user_count = db.query(User).count()
    print(f"📊 Current user count: {user_count}")
    db.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")

print("=" * 60)
