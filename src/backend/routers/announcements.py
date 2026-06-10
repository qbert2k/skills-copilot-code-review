"""
Announcement endpoints for the High School Management System API
"""

from fastapi import APIRouter
from typing import Optional, Dict, Any

from ..database import announcements_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


@router.get("/active", response_model=Optional[Dict[str, Any]])
def get_active_announcement() -> Optional[Dict[str, Any]]:
    """Get the active announcement to display on the site, or null if none is enabled"""
    announcement = announcements_collection.find_one({"enabled": True})
    if not announcement:
        return None
    return {
        "id": announcement["_id"],
        "message": announcement["message"],
        "enabled": announcement["enabled"]
    }
