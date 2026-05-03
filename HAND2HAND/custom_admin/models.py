from django.db import models
from donations.models import User  # Import User from donations app

# ===== Admin Activity Log =====
class AdminActivityLog(models.Model):
    ACTION_CHOICES = (
        ('user_approval', 'User Approval'),
        ('campaign_approval', 'Campaign Approval'),
        ('request_approval', 'Donation Request Approval'),
        ('user_deletion', 'User Deletion'),
        ('content_deletion', 'Content Deletion'),
        ('admin_creation', 'Admin Creation'),
    )
    
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="targeted_activities")
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.admin_user.username} - {self.action_type}"

# ===== System Settings =====
class SystemSettings(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

# ===== Admin Announcement =====
class AdminAnnouncement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    target_audience = models.CharField(max_length=50, choices=(
        ('all', 'All Users'),
        ('donors', 'Donors Only'),
        ('recipients', 'Recipients Only'),
        ('ngos', 'NGOs Only'),
        ('admins', 'Admins Only'),
    ), default='all')

    def __str__(self):
        return self.title