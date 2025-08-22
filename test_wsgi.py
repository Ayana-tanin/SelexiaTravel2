#!/usr/bin/env python3
"""
Test WSGI application loading
"""
import os
import sys
from pathlib import Path

def test_wsgi_loading():
    """Test if the WSGI application can be loaded"""
    try:
        # Add the project directory to Python path
        project_dir = Path(__file__).resolve().parent
        sys.path.insert(0, str(project_dir))
        
        print("🔍 Testing WSGI application loading...")
        print(f"   Project directory: {project_dir}")
        
        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selexia_travel.settings')
        
        print("   Setting Django settings module...")
        
        # Try to import the WSGI application
        from selexia_travel.wsgi import application
        
        print("✅ WSGI application loaded successfully!")
        print(f"   Application type: {type(application)}")
        
        return True
        
    except Exception as e:
        print(f"❌ WSGI application loading failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_wsgi_loading()
    sys.exit(0 if success else 1)
