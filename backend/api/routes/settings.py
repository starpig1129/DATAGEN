"""Settings API routes with persistence."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import models
from api.models.settings import SettingsRequest

# Create router
router = APIRouter()

# Settings file path
SETTINGS_FILE = Path(__file__).parent.parent.parent / "data" / "settings.json"


class SettingsResponse(BaseModel):
    """Settings response model."""
    settings: Dict[str, Any]
    lastModified: Optional[str] = None
    status: str = "ok"


def _load_settings() -> Dict[str, Any]:
    """Load settings from JSON file."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load settings: {e}")
    return {"settings": {}, "lastModified": None}


def _save_settings(data: Dict[str, Any]) -> None:
    """Save settings to JSON file."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@router.get("/api/settings")
async def get_settings():
    """Get current settings."""
    try:
        data = _load_settings()
        return SettingsResponse(
            settings=data.get("settings", {}),
            lastModified=data.get("lastModified"),
            status="ok"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load settings: {str(e)}")


@router.post("/api/settings")
async def update_settings(request: SettingsRequest):
    """Update settings."""
    try:
        timestamp = datetime.now().isoformat()
        data = {
            "settings": request.settings,
            "lastModified": timestamp
        }
        _save_settings(data)
        return {"status": "settings updated", "timestamp": timestamp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(e)}")