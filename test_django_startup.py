#!/usr/bin/env python3
"""
Test script to check Django startup and identify issues
"""
import os
import sys
import django
from pathlib import Path

def test_django_startup():
    """Test if Django can start properly"""
    try:
        # Add the project directory to Python path
        project_dir = Path(__file__).resolve().parent
        sys.path.insert(0, str(project_dir))
        
        print("🔍 Testing Django startup...")
        print(f"   Project directory: {project_dir}")
        print(f"   Python path: {sys.path[:3]}...")
        
        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selexia_travel.settings')
        
        print("   Setting Django settings module...")
        
        # Try to configure Django
        django.setup()
        
        print("✅ Django started successfully!")
        
        # Test basic Django functionality
        from django.conf import settings
        print(f"   Django version: {django.get_version()}")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"   CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
        print(f"   DATABASES: {settings.DATABASES['default']['ENGINE']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Django startup failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_django_startup()
    sys.exit(0 if success else 1)
