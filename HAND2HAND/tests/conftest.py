import pytest  # type: ignore
from selenium import webdriver  # type: ignore
from django.contrib.auth import get_user_model
from donations.models import (
    User, DonorRecipientProfile, Category, DonationItem,
    DonationImage, DonationClaim, DonationReview, RequestItem,
    DonationToRequest, Notification, ContactMessage, Reward, UserReward
)
from ngos.models import NGOProfile, Campaign, CampaignCategory, NGODonation, CampaignUpdate
from django.utils import timezone
from datetime import datetime, timedelta
import os
from tests.fixtures.test_data import get_sample_campaign_data

User = get_user_model()

# ===== Selenium driver fixture =====
@pytest.fixture(scope="session")
def driver():
    # Chrome options
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Enable later if needed
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")

    # ✅ FIX: No hardcoded path
    driver = webdriver.Chrome(options=options)

    driver.maximize_window()
    yield driver
    driver.quit()

# ===== User fixtures =====
@pytest.fixture
def donor_user(db):
    user = User.objects.create_user(
        username="donor1", 
        password="donorpass", 
        user_type="donor/recipient",
        email="donor1@test.com"
    )
    # Create profile
    DonorRecipientProfile.objects.create(
        user=user,
        full_name="John Doe",
        email="donor1@test.com",
        city_postal="Dhaka",
        address="123 Test Street",
        mobile_number="01712345678"
    )
    # Create user reward
    UserReward.objects.create(user=user, points=0)
    return user


@pytest.fixture
def donor_user2(db):
    user = User.objects.create_user(
        username="donor2", 
        password="donorpass2", 
        user_type="donor/recipient",
        email="donor2@test.com"
    )
    DonorRecipientProfile.objects.create(
        user=user,
        full_name="Jane Smith",
        email="donor2@test.com",
        city_postal="Chittagong",
        address="456 Test Avenue",
        mobile_number="01787654321"
    )
    UserReward.objects.create(user=user, points=0)
    return user


@pytest.fixture
def ngo_user(db):
    user = User.objects.create_user(
        username="ngo1",
        password="ngopass",
        user_type="ngo",
        email="ngo1@test.com"
    )
    user.is_approved = True  # ✅ NGO approved for testing
    user.save()
    
    # Create NGO profile
    NGOProfile.objects.create(
        user=user,
        ngo_name="Hope Foundation",
        email="ngo1@test.com",
        contact_person="Dr. Sarah Wilson",
        city_postal="Dhaka",
        address="789 NGO Street",
        ngo_type="Charity",
        social_link="https://facebook.com/hopefoundation",
        mobile_number="01711111111"
    )
    return user


@pytest.fixture
def pending_ngo_user(db):
    user = User.objects.create_user(
        username="pending_ngo",
        password="ngopass",
        user_type="ngo",
        email="pending@test.com"
    )
    user.is_approved = False  # Not approved yet
    user.save()
    
    NGOProfile.objects.create(
        user=user,
        ngo_name="Pending NGO",
        email="pending@test.com",
        contact_person="Pending Person",
        city_postal="Dhaka",
        address="Pending Address",
        ngo_type="Charity",
        mobile_number="01722222222"
    )
    return user


@pytest.fixture
def admin_user(db):
    user = User.objects.create_superuser(
        username="admin1", 
        password="adminpass", 
        user_type="admin",
        email="admin@test.com"
    )
    return user


# ===== Category fixtures =====
@pytest.fixture
def categories(db):
    """Create sample categories"""
    categories_data = [
        {"name": "Education", "description": "Books, school supplies, educational materials", "icon": "fa-solid fa-book"},
        {"name": "Food", "description": "Food items, groceries, meals", "icon": "fa-solid fa-utensils"},
        {"name": "Clothing", "description": "Clothes, shoes, accessories", "icon": "fa-solid fa-shirt"},
        {"name": "Electronics", "description": "Electronic devices, gadgets", "icon": "fa-solid fa-tv"},
        {"name": "Medical", "description": "Medical supplies, medicines", "icon": "fa-solid fa-pills"},
        {"name": "Furniture", "description": "Furniture, household items", "icon": "fa-solid fa-couch"},
    ]
    
    created_categories = []
    for cat_data in categories_data:
        category = Category.objects.create(**cat_data)
        created_categories.append(category)
    
    return created_categories


@pytest.fixture
def campaign_categories(db):
    """Create sample campaign categories"""
    categories_data = [
        {"name": "Emergency Relief", "description": "Emergency and disaster relief campaigns"},
        {"name": "Education", "description": "Educational and scholarship campaigns"},
        {"name": "Healthcare", "description": "Medical and healthcare campaigns"},
        {"name": "Community Development", "description": "Community development projects"},
    ]
    
    created_categories = []
    for cat_data in categories_data:
        category = CampaignCategory.objects.create(**cat_data)
        created_categories.append(category)
    
    return created_categories


# ===== Donation fixtures =====
@pytest.fixture
def sample_donations(db, donor_user, categories):
    """Create sample donation items"""
    donations = []
    
    # Education donation
    donation1 = DonationItem.objects.create(
        title="Mathematics Textbooks",
        description="Grade 10 mathematics textbooks in good condition",
        category=categories[0],  # Education
        quantity=5,
        donor=donor_user,
        location="Dhaka",
        urgency="medium",
        status="available"
    )
    donations.append(donation1)
    
    # Food donation
    donation2 = DonationItem.objects.create(
        title="Rice and Lentils",
        description="Fresh rice and lentils for families in need",
        category=categories[1],  # Food
        quantity=10,
        donor=donor_user,
        location="Chittagong",
        urgency="high",
        status="available"
    )
    donations.append(donation2)
    
    # Clothing donation
    donation3 = DonationItem.objects.create(
        title="Winter Clothes",
        description="Warm winter jackets and sweaters",
        category=categories[2],  # Clothing
        quantity=8,
        donor=donor_user,
        location="Dhaka",
        urgency="low",
        status="reserved"
    )
    donations.append(donation3)
    
    return donations


# ===== Campaign fixtures =====
@pytest.fixture
def sample_campaigns(db, ngo_user, campaign_categories):
    """Create sample campaigns"""
    campaigns = []
    
    # Approved campaign
    campaign1 = Campaign.objects.create(
        title="Emergency Flood Relief",
        description="Help flood victims with food and shelter",
        ngo=ngo_user,
        goal_amount=50000.00,
        category=campaign_categories[0],  # Emergency Relief
        status="approved",
        is_active=True,
        approved_at=timezone.now()
    )
    campaigns.append(campaign1)
    
    # Pending campaign
    campaign2 = Campaign.objects.create(
        title="School Building Project",
        description="Build a new school in rural area",
        ngo=ngo_user,
        goal_amount=100000.00,
        category=campaign_categories[1],  # Education
        status="pending",
        is_active=True
    )
    campaigns.append(campaign2)
    
    return campaigns


# Filtering test fixture
@pytest.fixture
def approved_campaigns(db, ngo_user, campaign_categories):
    campaigns = []
    for data in get_sample_campaign_data():  # সব sample_campaigns
        category_obj = next((c for c in campaign_categories if c.name == data["category"]), None)
        if not category_obj:
            continue
        campaign = Campaign.objects.create(
            title=data["title"],
            description=data["description"],
            ngo=ngo_user,
            goal_amount=data["goal_amount"],
            category=category_obj,
            status="approved",
            is_active=True,
            approved_at=timezone.now()
        )
        campaigns.append(campaign)
    return campaigns



# ===== Request fixtures =====
@pytest.fixture
def sample_requests(db, donor_user2, categories):
    """Create sample request items"""
    requests = []
    
    # Approved request
    request1 = RequestItem.objects.create(
        title="Need School Supplies",
        description="Urgent need for notebooks, pens, and pencils for underprivileged children",
        category=categories[0],  # Education
        quantity=50,
        requester=donor_user2,
        delivery_location="Dhaka",
        urgency="high",
        status="approved",
        approved_at=timezone.now()
    )
    requests.append(request1)
    
    # Pending request
    request2 = RequestItem.objects.create(
        title="Medical Equipment Needed",
        description="Need medical equipment for rural clinic",
        category=categories[4],  # Medical
        quantity=5,
        requester=donor_user2,
        delivery_location="Chittagong",
        urgency="medium",
        status="pending"
    )
    requests.append(request2)
    
    return requests


# ===== Reward fixtures =====
@pytest.fixture
def rewards(db):
    """Create reward tiers"""
    rewards_data = [
        {"name": "Silver", "points_required": 100, "tier_order": 1},
        {"name": "Gold", "points_required": 500, "tier_order": 2},
        {"name": "Diamond", "points_required": 1000, "tier_order": 3},
    ]
    
    created_rewards = []
    for reward_data in rewards_data:
        reward = Reward.objects.create(**reward_data)
        created_rewards.append(reward)
    
    return created_rewards


# ===== Test data cleanup =====
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up test files after each test"""
    yield
    # Cleanup will be handled by test_helpers.cleanup_temp_files()


# ===== Helper fixtures =====
@pytest.fixture
def test_image_path():
    """Create a test image file"""
    from tests.test_helpers import create_test_image
    return create_test_image()


@pytest.fixture
def test_document_path():
    """Create a test document file"""
    from tests.test_helpers import create_test_document
    return create_test_document()

















