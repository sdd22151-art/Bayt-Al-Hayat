from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.models.notification import Notification, UserNotificationRead, UserDeviceToken

router = APIRouter(tags=["Notifications"])


# ─── Schemas ───────────────────────────────────────────────────────────────────

class CreateNotificationRequest(BaseModel):
    title: str
    body: str
    type: str = "general"          # general, tip, reminder, update, promo
    target: str = "all"            # all, specific
    target_user_id: Optional[str] = None

class RegisterDeviceTokenRequest(BaseModel):
    device_token: str
    platform: str = "android"      # android, ios


# ─── Admin Guard ───────────────────────────────────────────────────────────────

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/admin/notifications", summary="Create & send a notification")
async def create_notification(
    body: CreateNotificationRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Admin creates a notification. It's stored in DB and available for users to fetch."""

    if body.target == "specific" and not body.target_user_id:
        raise HTTPException(status_code=400, detail="target_user_id is required when target is 'specific'")

    notification = Notification(
        title=body.title,
        body=body.body,
        type=body.type,
        target=body.target,
        target_user_id=body.target_user_id if body.target == "specific" else None,
        created_by=admin.id,
        is_active=True
    )

    db.add(notification)
    await db.commit()
    await db.refresh(notification)

    return {
        "message": "✅ Notification created successfully",
        "notification": {
            "id": str(notification.id),
            "title": notification.title,
            "type": notification.type,
            "target": notification.target,
            "created_at": notification.created_at.isoformat()
        }
    }


@router.get("/admin/notifications", summary="List all notifications (admin)")
async def list_notifications_admin(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Admin views all notifications with stats."""
    result = await db.execute(
        select(Notification)
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    notifications = result.scalars().all()

    # Get read counts for each notification
    read_counts_result = await db.execute(
        select(
            UserNotificationRead.notification_id,
            func.count(UserNotificationRead.id).label("read_count")
        )
        .group_by(UserNotificationRead.notification_id)
    )
    read_counts = {str(row.notification_id): row.read_count for row in read_counts_result.all()}

    # Total users count (for "all" target notifications)
    total_users = (await db.execute(select(func.count(User.id)).where(User.is_active == True))).scalar_one_or_none() or 0

    # Get creator names
    creator_ids = list(set(str(n.created_by) for n in notifications if n.created_by))
    creators_map = {}
    if creator_ids:
        creators_result = await db.execute(
            select(User.id, User.fullname).where(User.id.in_(creator_ids))
        )
        creators_map = {str(row.id): row.fullname for row in creators_result.all()}

    return [
        {
            "id": str(n.id),
            "title": n.title,
            "body": n.body,
            "type": n.type,
            "target": n.target,
            "target_user_id": str(n.target_user_id) if n.target_user_id else None,
            "is_active": n.is_active,
            "created_by_name": creators_map.get(str(n.created_by), "Unknown") if n.created_by else "System",
            "read_count": read_counts.get(str(n.id), 0),
            "total_audience": 1 if n.target == "specific" else total_users,
            "created_at": n.created_at.isoformat()
        }
        for n in notifications
    ]


@router.get("/admin/notifications/stats", summary="Notification statistics")
async def get_notification_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get notification stats for dashboard KPI cards."""
    total = (await db.execute(select(func.count(Notification.id)))).scalar_one_or_none() or 0
    active = (await db.execute(
        select(func.count(Notification.id)).where(Notification.is_active == True)
    )).scalar_one_or_none() or 0
    total_reads = (await db.execute(
        select(func.count(UserNotificationRead.id))
    )).scalar_one_or_none() or 0
    total_devices = (await db.execute(
        select(func.count(UserDeviceToken.id)).where(UserDeviceToken.is_active == True)
    )).scalar_one_or_none() or 0

    # Type breakdown
    type_result = await db.execute(
        select(Notification.type, func.count(Notification.id))
        .group_by(Notification.type)
    )
    type_breakdown = {row[0]: row[1] for row in type_result.all()}

    return {
        "total_notifications": total,
        "active_notifications": active,
        "total_reads": total_reads,
        "registered_devices": total_devices,
        "type_breakdown": type_breakdown
    }


@router.delete("/admin/notifications/{notification_id}", summary="Delete a notification")
async def delete_notification(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    await db.delete(notification)
    await db.commit()
    return {"message": "🗑️ Notification deleted successfully"}


@router.patch("/admin/notifications/{notification_id}/toggle", summary="Toggle notification active status")
async def toggle_notification(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_active = not notification.is_active
    await db.commit()
    return {
        "message": f"Notification is now {'Active' if notification.is_active else 'Inactive'}",
        "is_active": notification.is_active
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  USER ENDPOINTS (for Flutter app)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/notifications", summary="Get my notifications")
async def get_my_notifications(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notifications for the current user.
    Returns notifications targeted to 'all' OR specifically to this user.
    Each notification includes 'is_read' status.
    """
    # Get notifications: either targeted to all, or specifically to this user
    result = await db.execute(
        select(Notification)
        .where(
            Notification.is_active == True,
            or_(
                Notification.target == "all",
                and_(
                    Notification.target == "specific",
                    Notification.target_user_id == current_user.id
                )
            )
        )
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    notifications = result.scalars().all()

    # Get read status for this user
    notification_ids = [n.id for n in notifications]
    read_result = await db.execute(
        select(UserNotificationRead.notification_id)
        .where(
            UserNotificationRead.user_id == current_user.id,
            UserNotificationRead.notification_id.in_(notification_ids)
        )
    )
    read_ids = {str(row[0]) for row in read_result.all()}

    return [
        {
            "id": str(n.id),
            "title": n.title,
            "body": n.body,
            "type": n.type,
            "is_read": str(n.id) in read_ids,
            "created_at": n.created_at.isoformat()
        }
        for n in notifications
    ]


@router.get("/notifications/unread-count", summary="Get unread notification count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns the count of unread notifications for the current user (for badge display)."""
    # Subquery: notification IDs this user has read
    read_subquery = (
        select(UserNotificationRead.notification_id)
        .where(UserNotificationRead.user_id == current_user.id)
    ).subquery()

    count = (await db.execute(
        select(func.count(Notification.id))
        .where(
            Notification.is_active == True,
            or_(
                Notification.target == "all",
                and_(
                    Notification.target == "specific",
                    Notification.target_user_id == current_user.id
                )
            ),
            Notification.id.notin_(select(read_subquery))
        )
    )).scalar_one_or_none() or 0

    return {"unread_count": count}


@router.post("/notifications/{notification_id}/read", summary="Mark a notification as read")
async def mark_as_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a single notification as read for the current user."""
    # Check notification exists
    notif = (await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )).scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    # Check if already read
    existing = (await db.execute(
        select(UserNotificationRead).where(
            UserNotificationRead.user_id == current_user.id,
            UserNotificationRead.notification_id == notification_id
        )
    )).scalar_one_or_none()

    if not existing:
        read_record = UserNotificationRead(
            user_id=current_user.id,
            notification_id=notification_id
        )
        db.add(read_record)
        await db.commit()

    return {"message": "Marked as read"}


@router.post("/notifications/read-all", summary="Mark all notifications as read")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all unread notifications as read for the current user."""
    # Get all notifications for this user
    result = await db.execute(
        select(Notification.id)
        .where(
            Notification.is_active == True,
            or_(
                Notification.target == "all",
                and_(
                    Notification.target == "specific",
                    Notification.target_user_id == current_user.id
                )
            )
        )
    )
    all_notif_ids = [row[0] for row in result.all()]

    # Get already-read IDs
    read_result = await db.execute(
        select(UserNotificationRead.notification_id)
        .where(
            UserNotificationRead.user_id == current_user.id,
            UserNotificationRead.notification_id.in_(all_notif_ids)
        )
    )
    already_read = {row[0] for row in read_result.all()}

    # Create read records for unread ones
    new_reads = []
    for nid in all_notif_ids:
        if nid not in already_read:
            new_reads.append(UserNotificationRead(
                user_id=current_user.id,
                notification_id=nid
            ))

    if new_reads:
        db.add_all(new_reads)
        await db.commit()

    return {"message": f"Marked {len(new_reads)} notifications as read"}


# ═══════════════════════════════════════════════════════════════════════════════
#  DEVICE TOKEN ENDPOINTS (for FCM Push Notifications)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/notifications/register-device", summary="Register FCM device token")
async def register_device_token(
    body: RegisterDeviceTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Flutter app calls this on startup to register/update the device FCM token.
    This enables push notifications to be sent to the device.
    """
    # Check if token already exists for this user
    existing = (await db.execute(
        select(UserDeviceToken).where(
            UserDeviceToken.user_id == current_user.id,
            UserDeviceToken.device_token == body.device_token
        )
    )).scalar_one_or_none()

    if existing:
        existing.is_active = True
        existing.updated_at = datetime.utcnow()
    else:
        # Deactivate old tokens for same user+platform (one device per platform)
        old_tokens_result = await db.execute(
            select(UserDeviceToken).where(
                UserDeviceToken.user_id == current_user.id,
                UserDeviceToken.platform == body.platform
            )
        )
        for old_token in old_tokens_result.scalars().all():
            old_token.is_active = False

        new_token = UserDeviceToken(
            user_id=current_user.id,
            device_token=body.device_token,
            platform=body.platform,
            is_active=True
        )
        db.add(new_token)

    await db.commit()
    return {"message": "✅ Device token registered successfully"}


@router.delete("/notifications/unregister-device", summary="Unregister device token (on logout)")
async def unregister_device_token(
    body: RegisterDeviceTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Flutter app calls this on logout to stop receiving push notifications."""
    result = await db.execute(
        select(UserDeviceToken).where(
            UserDeviceToken.user_id == current_user.id,
            UserDeviceToken.device_token == body.device_token
        )
    )
    token = result.scalar_one_or_none()
    if token:
        token.is_active = False
        await db.commit()

    return {"message": "Device token unregistered"}
