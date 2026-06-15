"""
Announcement endpoints for the High School Management System API
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)

DATE_FORMAT = "%Y-%m-%d"


def _resolve_announcement_filter(announcement_id: str) -> Dict[str, Any]:
    try:
        return {"_id": ObjectId(announcement_id)}
    except Exception:
        return {"_id": announcement_id}


def _to_date(value: Any) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value:
        return datetime.strptime(value, DATE_FORMAT).date()
    return None


def _parse_date(field_name: str, value: Optional[str], required: bool = False) -> Optional[date]:
    if value in (None, ""):
        if required:
            raise HTTPException(
                status_code=422,
                detail=f"{field_name} is required",
            )
        return None

    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} must use the YYYY-MM-DD format",
        ) from exc


def _require_authenticated_user(teacher_username: Optional[str]) -> Dict[str, Any]:
    if not teacher_username:
        raise HTTPException(
            status_code=401,
            detail="Authentication required for this action",
        )

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(
            status_code=401,
            detail="Invalid teacher credentials",
        )
    return teacher


def _announcement_is_active(announcement: Dict[str, Any]) -> bool:
    today = date.today()
    start_date = _to_date(announcement.get("start_date"))
    expiration_date = _to_date(announcement.get("expiration_date"))

    if not announcement.get("enabled", True):
        return False
    if expiration_date is None or expiration_date < today:
        return False
    if start_date is not None and start_date > today:
        return False
    return True


def _serialize_announcement(announcement: Dict[str, Any]) -> Dict[str, Any]:
    start_date = _to_date(announcement.get("start_date"))
    expiration_date = _to_date(announcement.get("expiration_date"))

    return {
        "id": str(announcement["_id"]),
        "message": announcement.get("message", ""),
        "enabled": announcement.get("enabled", True),
        "start_date": start_date.isoformat() if start_date else None,
        "expiration_date": expiration_date.isoformat() if expiration_date else None,
        "is_active": _announcement_is_active(announcement),
    }


def _build_announcement_payload(announcement: Dict[str, Any]) -> Dict[str, Any]:
    message = (announcement.get("message") or "").strip()
    if not message:
        raise HTTPException(
            status_code=422,
            detail="Announcement message is required",
        )

    start_date = _parse_date("start_date", announcement.get("start_date"))
    expiration_date = _parse_date(
        "expiration_date", announcement.get("expiration_date"), required=True
    )

    if start_date is not None and start_date > expiration_date:
        raise HTTPException(
            status_code=422,
            detail="Start date must be on or before the expiration date",
        )

    return {
        "message": message,
        "enabled": bool(announcement.get("enabled", True)),
        "start_date": start_date.isoformat() if start_date else None,
        "expiration_date": expiration_date.isoformat(),
        "updated_at": datetime.utcnow(),
    }


@router.get("/active", response_model=Optional[Dict[str, Any]])
def get_active_announcement() -> Optional[Dict[str, Any]]:
    """Get the active announcement to display on the site, or null if none is enabled."""
    active_announcements: List[Dict[str, Any]] = []

    for announcement in announcements_collection.find({"enabled": True}):
        if _announcement_is_active(announcement):
            active_announcements.append(announcement)

    if not active_announcements:
        return None

    active_announcements.sort(
        key=lambda announcement: (
            _to_date(announcement.get("expiration_date")) or date.max,
            _to_date(announcement.get("start_date")) or date.min,
            str(announcement.get("_id", "")),
        )
    )
    return _serialize_announcement(active_announcements[0])


@router.get("")
def list_announcements(teacher_username: str) -> List[Dict[str, Any]]:
    """List all announcements for the management dialog."""
    _require_authenticated_user(teacher_username)
    announcements = sorted(
        announcements_collection.find(),
        key=lambda announcement: (
            _to_date(announcement.get("expiration_date")) or date.max,
            _to_date(announcement.get("start_date")) or date.min,
            str(announcement.get("_id", "")),
        ),
    )
    return [_serialize_announcement(announcement) for announcement in announcements]


@router.post("")
def create_announcement(
    announcement: Dict[str, Any], teacher_username: str
) -> Dict[str, Any]:
    """Create a new announcement."""
    _require_authenticated_user(teacher_username)
    payload = _build_announcement_payload(announcement)
    result = announcements_collection.insert_one(payload)
    stored_announcement = announcements_collection.find_one({"_id": result.inserted_id})
    return _serialize_announcement(stored_announcement)


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: str, announcement: Dict[str, Any], teacher_username: str
) -> Dict[str, Any]:
    """Update an existing announcement."""
    _require_authenticated_user(teacher_username)
    announcement_filter = _resolve_announcement_filter(announcement_id)
    existing = announcements_collection.find_one(announcement_filter)

    if not existing:
        raise HTTPException(status_code=404, detail="Announcement not found")

    payload = _build_announcement_payload(announcement)
    announcements_collection.update_one(announcement_filter, {"$set": payload})
    updated_announcement = announcements_collection.find_one(announcement_filter)
    return _serialize_announcement(updated_announcement)


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str, teacher_username: str) -> Dict[str, str]:
    """Delete an announcement."""
    _require_authenticated_user(teacher_username)
    announcement_filter = _resolve_announcement_filter(announcement_id)
    result = announcements_collection.delete_one(announcement_filter)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted"}