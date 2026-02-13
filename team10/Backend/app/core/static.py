"""Static file serving configuration for audio files."""
from fastapi.staticfiles import StaticFiles
from pathlib import Path


def configure_static_files(app):
    """Configure static file serving for audio files."""
    static_path = Path(__file__).parent.parent.parent / "static" / "ListeningItems"
    
    if static_path.exists():
        app.mount("/static/ListeningItems", StaticFiles(directory=str(static_path)), name="listening_items")
