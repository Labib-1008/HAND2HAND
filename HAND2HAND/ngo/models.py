from django.db import models
from donations.models import User  # Import User from donations app
from django.conf import settings


# ===== NGO Profile =====
class NGOProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ngo_name = models.CharField(max_length=200, blank=True, null=True)
    reg_certificate = models.FileField(upload_to='documents/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    contact_person = models.CharField(max_length=200, blank=True, null=True)
    nid_birth_certificate = models.FileField(upload_to='documents/', blank=True, null=True)
    city_postal = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    ngo_type = models.CharField(max_length=100, blank=True, null=True)
    social_link = models.URLField(blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)

    is_verified = models.BooleanField(default=False)  # Additional verification flag

    def __str__(self):
        return self.ngo_name or self.user.username

# ===== Campaign (NGO) - REQUIRES ADMIN APPROVAL =====

class Campaign(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    ngo = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'ngo', 'is_approved': True},
        related_name="campaigns"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="campaigns/", blank=True, null=True)
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    collected_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    category = models.ForeignKey(
        'CampaignCategory',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='campaigns'
    )
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        ngo_name = getattr(self.ngo.ngoprofile, "ngo_name", None)
        return f"{self.title} by {ngo_name or self.ngo.username}"



class CampaignCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Campaign Categories"



class CampaignUpdate(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="updates")
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.campaign.title})"



    


# ===== NGO Donation (Donations made to NGO campaigns) =====
class NGODonation(models.Model):
    campaign = models.ForeignKey(
        'Campaign',
        on_delete=models.CASCADE,
        related_name="donations"
    )
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ngo_donations"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    donated_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)
    payer_name = models.CharField(max_length=255, blank=True, null=True)
    account_input = models.CharField(max_length=255, blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)

    # ===== SSLCommerz Integration Fields =====
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="SSLCommerz"
    )  # e.g., SSLCommerz
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )  # SSLCommerz transaction ID
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )

    def __str__(self):
        return f"Donation of {self.amount} to {self.campaign.title} by {self.donor.username}"
