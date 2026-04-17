import uuid
from datetime import datetime
from sqlmodel import select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from app.notifications.models import EventLike, EventComment, Notification, NotificationPreference, NotificationType


class NotificationService:
    async def like_event(self, event_id: uuid.UUID, user_id: uuid.UUID, session: AsyncSession) -> bool:
        """Like an event. Returns True if liked, False if unliked."""
        # Check if user already liked this event
        sql = select(EventLike).where(
            EventLike.event_id == event_id,
            EventLike.user_id == user_id
        )
        result = await session.exec(sql)
        existing_like = result.one_or_none()

        if existing_like:
            # Unlike: remove the like
            await session.delete(existing_like)
            await session.commit()
            return False
        else:
            # Like: add new like
            new_like = EventLike(event_id=event_id, user_id=user_id)
            session.add(new_like)
            await session.commit()
            return True

    async def add_comment(self, event_id: uuid.UUID, user_id: uuid.UUID, comment: str, session: AsyncSession) -> EventComment:
        """Add a comment to an event."""
        new_comment = EventComment(
            event_id=event_id,
            user_id=user_id,
            comment=comment
        )
        session.add(new_comment)
        await session.commit()
        await session.refresh(new_comment)
        return new_comment

    async def get_event_likes_count(self, event_id: uuid.UUID, session: AsyncSession) -> int:
        """Get the number of likes for an event."""
        sql = select(EventLike).where(EventLike.event_id == event_id)
        result = await session.exec(sql)
        likes = result.all()
        return len(likes)

    async def get_event_comments(self, event_id: uuid.UUID, session: AsyncSession, limit: int = 10):
        """Get comments for an event."""
        sql = select(EventComment).where(EventComment.event_id == event_id).order_by(
            EventComment.created_at.desc()).limit(limit)
        result = await session.exec(sql)
        comments = result.all()
        return comments

    async def is_event_liked_by_user(self, event_id: uuid.UUID, user_id: uuid.UUID, session: AsyncSession) -> bool:
        """Check if an event is liked by a specific user."""
        sql = select(EventLike).where(
            EventLike.event_id == event_id,
            EventLike.user_id == user_id
        )
        result = await session.exec(sql)
        like = result.one_or_none()
        return like is not None

    # New notification methods
    async def create_notification(self, user_id: uuid.UUID, notification_type: NotificationType,
                                  title: str, message: str, related_id: uuid.UUID = None,
                                  session: AsyncSession = None) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            related_id=related_id
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    async def get_user_notifications(self, user_id: uuid.UUID, session: AsyncSession,
                                     limit: int = 50, unread_only: bool = False):
        """Get notifications for a user."""
        sql = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            sql = sql.where(Notification.is_read == False)
        sql = sql.order_by(Notification.created_at.desc()).limit(limit)
        result = await session.exec(sql)
        return result.all()

    async def mark_notification_read(self, notification_id: uuid.UUID, session: AsyncSession):
        """Mark a notification as read."""
        sql = update(Notification).where(Notification.id ==
                                         notification_id).values(is_read=True)
        await session.exec(sql)
        await session.commit()

    async def mark_all_notifications_read(self, user_id: uuid.UUID, session: AsyncSession):
        """Mark all notifications as read for a user."""
        sql = update(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).values(is_read=True)
        await session.exec(sql)
        await session.commit()

    async def get_unread_count(self, user_id: uuid.UUID, session: AsyncSession) -> int:
        """Get count of unread notifications for a user."""
        sql = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
        result = await session.exec(sql)
        notifications = result.all()
        return len(notifications)

    async def get_or_create_preferences(self, user_id: uuid.UUID, session: AsyncSession) -> NotificationPreference:
        """Get or create notification preferences for a user."""
        sql = select(NotificationPreference).where(
            NotificationPreference.user_id == user_id)
        result = await session.exec(sql)
        preferences = result.one_or_none()

        if not preferences:
            preferences = NotificationPreference(user_id=user_id)
            session.add(preferences)
            await session.commit()
            await session.refresh(preferences)

        return preferences

    async def update_preferences(self, user_id: uuid.UUID, preferences_data: dict, session: AsyncSession):
        """Update notification preferences for a user."""
        sql = update(NotificationPreference).where(
            NotificationPreference.user_id == user_id
        ).values(**preferences_data)
        await session.exec(sql)
        await session.commit()

    async def create_event_notification(self, event_id: uuid.UUID, event_name: str,
                                        notification_type: NotificationType, session: AsyncSession):
        """Create notifications for all users about an event (except the creator)."""
        # This would typically be called when events are created/updated
        # For now, we'll create a system notification
        pass

    async def cleanup_old_notifications(self, days: int = 30, session: AsyncSession = None):
        """Clean up old read notifications."""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)

        sql = select(Notification).where(
            Notification.is_read == True,
            Notification.created_at < cutoff_date
        )
        result = await session.exec(sql)
        old_notifications = result.all()

        for notification in old_notifications:
            await session.delete(notification)

        await session.commit()
        return len(old_notifications)
