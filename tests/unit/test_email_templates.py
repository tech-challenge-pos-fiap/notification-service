import pytest

from app.infrastructure.email.email_templates import get_email_template


class TestEmailTemplates:
    """Tests for email template rendering"""
    
    def test_verify_email_template(self):
        """Test verify email template rendering"""
        context = {
            "user_name": "John Doe",
            "verification_link": "https://example.com/verify?token=123",
        }
        
        html = get_email_template("verify_email", context)
        
        assert "John Doe" in html
        assert "https://example.com/verify?token=123" in html
        assert "<!DOCTYPE html>" in html
    
    def test_password_reset_template(self):
        """Test password reset template rendering"""
        context = {
            "user_name": "Jane Doe",
            "reset_link": "https://example.com/reset?token=456",
        }
        
        html = get_email_template("password_reset", context)
        
        assert "Jane Doe" in html
        assert "https://example.com/reset?token=456" in html
    
    def test_job_completed_template(self):
        """Test job completed template rendering"""
        context = {
            "user_name": "John Doe",
            "job_id": "job123",
            "video_name": "my_video.mp4",
            "processing_time": "5 minutes",
            "video_link": "https://example.com/video/123",
        }
        
        html = get_email_template("job_completed", context)
        
        assert "John Doe" in html
        assert "job123" in html
        assert "my_video.mp4" in html
        assert "5 minutes" in html
    
    def test_template_not_found(self):
        """Test error when template not found"""
        with pytest.raises(ValueError, match="Template 'nonexistent' not found"):
            get_email_template("nonexistent", {})
