"""Legacy entrypoint.

Use backend.app.main with uvicorn for the new orchestrated service.
"""

from backend.app.main import app

__all__ = ['app']
