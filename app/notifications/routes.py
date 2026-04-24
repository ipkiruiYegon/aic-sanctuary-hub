from datetime import datetime
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from app.core.templates import templates
from app.db.database import get_session
from app.events.service import EventService
from app.notifications.services import NotificationService
from app.notifications.models import NotificationPreference

notifications_router = APIRouter()

event_services = EventService()
notification_services = NotificationService()


@notifications_router.get("")
async def get_notifications(request: Request, session: AsyncSession = Depends(get_session)):
    current_time = datetime.now()
    current_user = request.state.user["user"]["user_id"]

    # Get upcoming events (approved events with date_from >= current_time)
    upcoming_events = await event_services.get_upcoming_events(session, current_time)

    # Get past events (approved events with date_to < current_time)
    past_events = await event_services.get_past_events(session, current_time)

    # Get user notifications
    user_notifications = await notification_services.get_user_notifications(current_user, session, limit=20)

    # Get unread count
    unread_count = await notification_services.get_unread_count(current_user, session)

    # Get notification preferences
    preferences = await notification_services.get_or_create_preferences(current_user, session)

    return templates.TemplateResponse(
        "notifications.html",
        {
            "request": request,
            "upcoming_events": upcoming_events,
            "past_events": past_events,
            "notifications": user_notifications,
            "unread_count": unread_count,
            "preferences": preferences
        }
    )


@notifications_router.get("/api/recent")
async def get_recent_notifications(request: Request, session: AsyncSession = Depends(get_session)):
    """API endpoint to get recent notifications for navbar dropdown."""
    current_user = request.state.user["user"]["user_id"]
    notifications = await notification_services.get_user_notifications(current_user, session, limit=5)

    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            "id": str(notification.id),
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat()
        })

    return {"notifications": notifications_data}


@notifications_router.post("/mark-read/{notification_id}")
async def mark_notification_read(notification_id: UUID, session: AsyncSession = Depends(get_session)):
    """Mark a specific notification as read."""
    await notification_services.mark_notification_read(notification_id, session)
    return {"success": True}


@notifications_router.post("/mark-all-read")
async def mark_all_notifications_read(request: Request, session: AsyncSession = Depends(get_session)):
    """Mark all notifications as read for current user."""
    current_user = request.state.user["user"]["user_id"]
    await notification_services.mark_all_notifications_read(current_user, session)
    return {"success": True}


@notifications_router.get("/preferences")
async def get_notification_preferences(request: Request, session: AsyncSession = Depends(get_session)):
    """Get notification preferences for current user."""
    current_user = request.state.user["user"]["user_id"]
    preferences = await notification_services.get_or_create_preferences(current_user, session)
    return {"preferences": preferences}


@notifications_router.get("/api/unread-count")
async def get_unread_count_api(request: Request, session: AsyncSession = Depends(get_session)):
    current_user = request.state.user["user"]["user_id"]
    unread_count = await notification_services.get_unread_count(current_user, session)
    return {"unread_count": unread_count}


@notifications_router.post("/preferences")
async def update_notification_preferences(
    request: Request,
    preferences: NotificationPreference,
    session: AsyncSession = Depends(get_session)
):
    """Update notification preferences for current user."""
    current_user = request.state.user["user"]["user_id"]
    preferences_data = preferences.model_dump(exclude={'id', 'user_id'})
    await notification_services.update_preferences(current_user, preferences_data, session)
    return {"success": True, "message": "Preferences updated successfully"}


@notifications_router.get("/events/{event_id}/like")
async def get_event_like_status(
    request: Request,
    event_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    current_user = request.state.user["user"]["user_id"]

    try:
        likes_count = await notification_services.get_event_likes_count(event_id, session)
        liked = await notification_services.is_event_liked_by_user(event_id, current_user, session)

        return {
            "success": True,
            "liked": liked,
            "likes_count": likes_count
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@notifications_router.post("/events/{event_id}/like")
async def like_event(
    request: Request,
    event_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    current_user = request.state.user["user"]["user_id"]

    try:
        liked = await notification_services.like_event(event_id, current_user, session)
        likes_count = await notification_services.get_event_likes_count(event_id, session)

        return {
            "success": True,
            "liked": liked,
            "likes_count": likes_count
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@notifications_router.post("/events/{event_id}/comment")
async def add_comment(
    request: Request,
    event_id: UUID,
    comment: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    current_user = request.state.user["user"]["user_id"]

    try:
        new_comment = await notification_services.add_comment(event_id, current_user, comment, session)

        return {
            "success": True,
            "comment": {
                "id": str(new_comment.id),
                "comment": new_comment.comment,
                "created_at": new_comment.created_at.isoformat(),
                "user": {
                    "first_name": request.state.user["user"]["first_name"],
                    "last_name": request.state.user["user"]["last_name"]
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@notifications_router.get("/events/{event_id}/comments")
async def get_event_comments(
    event_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    try:
        comments = await notification_services.get_event_comments(event_id, session)
        comments_data = []

        for comment in comments:
            comments_data.append({
                "id": str(comment.id),
                "comment": comment.comment,
                "created_at": comment.created_at.isoformat(),
                "user": {
                    "first_name": comment.user.first_name,
                    "last_name": comment.user.last_name
                }
            })

        return {"comments": comments_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
