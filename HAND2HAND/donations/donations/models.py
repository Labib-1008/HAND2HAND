from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


# ===== User Model (in donations app) =====
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('donor/recipient', 'Donor/Recipient'),
        ('ngo', 'NGO'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, blank=True, null=True)
    is_approved = models.BooleanField(default=False)  # For NGO approval

    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True) # Profile picture field

    def save(self, *args, **kwargs):
        if self.is_superuser:   # ✅ superuser হলে auto admin হবে
            self.user_type = 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

# ===== Donor / Recipient Profile =====
class DonorRecipientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    nid_birth_certificate = models.FileField(upload_to='documents/', blank=True, null=True)
    city_postal = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.full_name or self.user.username

# ===== Category Model =====
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

# ===== Donation Item Model  =====
class DonationItem(models.Model):
    URGENCY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('claimed', 'Claimed'),
        ('expired', 'Expired'),
    )
    
    # Basic information
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    
    # Donor information
    donor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'donor/recipient'},
        related_name="donated_items"
    )
    
    # Location information
    location = models.CharField(max_length=200)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    # Item status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    urgency = models.CharField(max_length=10, choices=URGENCY_LEVELS, default='medium')
    
    # Dates
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    
    # Flags
    notify_immediately = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} by {self.donor.username}"
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return 0
    
    @property
    def total_reviews(self):
        return self.reviews.count()
    
    @property
    def is_available(self):
        return self.status == 'available'
    
    class Meta:
        ordering = ['-created_at']

# ===== Donation Image Model =====
class DonationImage(models.Model):
    donation_item = models.ForeignKey(DonationItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='donation_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.donation_item.title}"

# ===== Donation Claim Model =====
class DonationClaim(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    donation_item = models.ForeignKey(DonationItem, on_delete=models.CASCADE, related_name='claims')
    claimant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'donor/recipient'},
        related_name='claims_made'
    )
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For scheduled pickup/delivery
    preferred_date = models.DateTimeField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"Claim for {self.donation_item.title} by {self.claimant.username}"
    
    @property
    def can_review(self):
        return self.status == 'completed' and not hasattr(self, 'review')
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['donation_item', 'claimant']
    def save(self, *args, **kwargs):
     self.status = self.status.strip().lower()
     super().save(*args, **kwargs)


# ===== Donation Review Model =====
class DonationReview(models.Model):
    donation_item = models.ForeignKey(
        DonationItem, on_delete=models.CASCADE, related_name='reviews'
    )
    claimant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'donor/recipient'},
        related_name='reviews_given'
    )
    claim = models.OneToOneField(
        DonationClaim, on_delete=models.CASCADE, related_name='review',
        null=True,   # nullable again
        blank=True
    )

    rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.rating} star review for {self.donation_item.title} by {self.claimant.username}"


# ===== Request Item (Normal User) - REQUIRES ADMIN APPROVAL =====
class RequestItem(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    URGENCY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'donor/recipient'},
        related_name="requests"
    )
    image = models.ImageField(upload_to="request_items/", blank=True, null=True)
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    description = models.TextField()
    needed_before = models.DateField(blank=True, null=True)
    delivery_location = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    notify_immediately = models.BooleanField(default=False)
    urgency = models.CharField(
        max_length=6,
        choices=URGENCY_CHOICES,
        default='low',
        help_text="Set the urgency of this request."
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.requester.username}"
    


# ===== Donation to Request Model =====

class DonationToRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),       # Donor just donated
        ('completed', 'Completed'),   # Requester received it
        ('cancelled', 'Cancelled'),   # Donor cancelled
    )

    donor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='donations_to_requests'
    )
    request_item = models.ForeignKey(
        RequestItem, 
        on_delete=models.CASCADE, 
        related_name='donations'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    image = models.ImageField(
        upload_to='donations_to_request/', 
        blank=True, 
        null=True
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} to {self.request_item.title} by {self.donor.username}"

    class Meta:
        ordering = ['-created_at']


# ===== Notification Model =====
class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    message = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}"
    

class ContactMessage(models.Model):
     name = models.CharField(max_length=100)
     email = models.EmailField()
     message = models.TextField()
     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
        return f"Message from {self.name}"
     

class Reward(models.Model):
    REWARD_CHOICES = (
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('Diamond', 'Diamond'),
    )
    
    name = models.CharField(max_length=20, choices=REWARD_CHOICES)
    points_required = models.IntegerField()
    tier_order = models.IntegerField(default=0)  # lower = lower tier

    def __str__(self):
        return self.name
    

class UserReward(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reward')
    points = models.IntegerField(default=0)
    rewards = models.ManyToManyField(Reward, blank=True)
    
    def add_points(self, amount):
        self.points += amount
        self.save()
        self.check_rewards()
    
    def check_rewards(self):
        for reward in Reward.objects.all():
            if self.points >= reward.points_required and reward not in self.rewards.all():
                self.rewards.add(reward)
    
    def next_reward(self):
        remaining_rewards = Reward.objects.filter(points_required__gt=self.points).order_by('points_required')
        return remaining_rewards.first() if remaining_rewards.exists() else None

    def progress_percentage(self):
        next_reward = self.next_reward()
        if not next_reward:
            return 100
        prev_points = max([r.points_required for r in Reward.objects.filter(points_required__lte=self.points)] + [0])
        return int((self.points - prev_points) / (next_reward.points_required - prev_points) * 100)
