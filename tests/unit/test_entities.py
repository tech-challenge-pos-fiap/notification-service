from app.domain.entities.notification import (
    Notification,
    NotificationType,
    NotificationStatus,
)


class TestNotification:
    """Tests for Notification entity"""
    
    def test_notification_creation(self):
        """Test creating a notification"""
        notification = Notification(
            id="123",
            user_id=1,
            recipient_email="user@example.com",
            notification_type=NotificationType.EMAIL_VERIFICATION,
            template="verify_email",
            subject="Verify your email",
            data={"link": "https://example.com"},
        )
        
        assert notification.id == "123"
        assert notification.user_id == 1
        assert notification.recipient_email == "user@example.com"
        assert notification.status == NotificationStatus.PENDING
        assert notification.retry_count == 0
        assert notification.created_at is not None
    
    def test_mark_as_sent(self):
        """Test marking notification as sent"""
        notification = Notification(
            id="123",
            user_id=1,
            recipient_email="user@example.com",
            notification_type=NotificationType.EMAIL_VERIFICATION,
            template="verify_email",
            subject="Verify your email",
            data={},
        )
        
        notification.mark_as_sent()
        
        assert notification.status == NotificationStatus.SENT
        assert notification.error_message is None
    
    def test_mark_as_failed(self):
        """Test marking notification as failed"""
        notification = Notification(
            id="123",
            user_id=1,
            recipient_email="user@example.com",
            notification_type=NotificationType.EMAIL_VERIFICATION,
            template="verify_email",
            subject="Verify your email",
            data={},
        )
        
        error = "SMTP connection failed"
        notification.mark_as_failed(error)
        
        assert notification.status == NotificationStatus.FAILED
        assert notification.error_message == error
    
    def test_mark_for_retry(self):
        """Test marking notification for retry"""
        notification = Notification(
            id="123",
            user_id=1,
            recipient_email="user@example.com",
            notification_type=NotificationType.EMAIL_VERIFICATION,
            template="verify_email",
            subject="Verify your email",
            data={},
        )
        
        notification.mark_for_retry()
        
        assert notification.status == NotificationStatus.RETRYING
        assert notification.retry_count == 1
    
    def test_can_retry(self):
        """Test checking if notification can be retried"""
        notification = Notification(
            id="123",
            user_id=1,
            recipient_email="user@example.com",
            notification_type=NotificationType.EMAIL_VERIFICATION,
            template="verify_email",
            subject="Verify your email",
            data={},
        )
        
        assert notification.can_retry(max_retries=3) is True
        
        notification.retry_count = 3
        assert notification.can_retry(max_retries=3) is False
