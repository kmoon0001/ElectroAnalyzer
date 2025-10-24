import sys
sys.path.insert(0, '.')
try:
    print("Starting API import test...")
    from src.api.main import app
    print("SUCCESS: App imported successfully")
    print(f"App: {app}")
    print(f"App title: {app.title}")
except Exception as e:
    print(f"ERROR during import: {e}")
    import traceback
    traceback.print_exc()
