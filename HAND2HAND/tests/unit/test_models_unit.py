import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from donations.models import (
    User,
    DonorRecipientProfile,
    Category,
    DonationItem,
    DonationClaim,
    DonationReview,
    RequestItem,
    DonationToRequest,
    Notification,
    Reward,
    UserReward,
)
from ngos.models import NGOProfile, Campaign, CampaignCategory, NGODonation, CampaignUpdate


pytestmark = pytest.mark.django_db


# ---------- Small factory helpers ----------

def make_user(username="user1", user_type="donor/recipient", password="TestPass123"):
    return User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password=password,
        user_type=user_type,
    )


def make_admin(username="admin1"):
    return User.objects.create_superuser(
        username=username,
        email=f"{username}@test.com",
        password="AdminPass123",
    )


def make_category(name="Education"):
    return Category.objects.create(name=name, description=f"{name} items", icon="fa-book")


def make_donation(title="School Books", donor=None, category=None, status="available"):
    donor = donor or make_user("donor")
    category = category or make_category()
    return DonationItem.objects.create(
        title=title,
        description="Useful donation item",
        category=category,
        quantity=2,
        donor=donor,
        location="Dhaka",
        urgency="medium",
        status=status,
    )


def make_request(title="Need Books", requester=None, category=None, status="pending"):
    requester = requester or make_user("requester")
    category = category or make_category()
    return RequestItem.objects.create(
        requester=requester,
        title=title,
        category=category,
        quantity=1,
        description="Need this item urgently",
        delivery_location="Dhaka",
        contact_number="01712345678",
        urgency="high",
        status=status,
    )


def make_ngo(username="ngo1", approved=True):
    user = make_user(username=username, user_type="ngo")
    user.is_approved = approved
    user.save()
    NGOProfile.objects.create(
        user=user,
        ngo_name="Hope Foundation",
        email=user.email,
        contact_person="Contact Person",
        city_postal="Dhaka",
        address="NGO address",
        ngo_type="Charity",
        mobile_number="01700000000",
    )
    return user


def make_campaign(title="Food Campaign", ngo=None, category=None, status="pending"):
    ngo = ngo or make_ngo()
    category = category or CampaignCategory.objects.create(name="Emergency Relief")
    return Campaign.objects.create(
        ngo=ngo,
        title=title,
        description="Campaign description",
        goal_amount=10000,
        category=category,
        status=status,
        is_active=True,
    )


# ---------- User and profile model tests ----------

def test_superuser_save_sets_user_type_admin():
    admin = make_admin()
    assert admin.user_type == "admin"
    assert admin.is_superuser is True


def test_user_str_returns_username():
    user = make_user(username="rahim")
    assert str(user) == "rahim"


def test_donor_profile_str_uses_full_name_then_username():
    user = make_user(username="donor_a")
    profile = DonorRecipientProfile.objects.create(user=user, full_name="Donor A")
    assert str(profile) == "Donor A"

    profile.full_name = ""
    profile.save()
    assert str(profile) == "donor_a"


# ---------- Donation model tests ----------

def test_donation_item_str_and_availability():
    donor = make_user(username="donor_b")
    item = make_donation(title="Winter Jacket", donor=donor, status="available")

    assert str(item) == "Winter Jacket by donor_b"
    assert item.is_available is True

    item.status = "claimed"
    item.save()
    assert item.is_available is False


def test_donation_average_rating_and_total_reviews():
    item = make_donation()
    claimant1 = make_user(username="claimant1")
    claimant2 = make_user(username="claimant2")

    DonationReview.objects.create(donation_item=item, claimant=claimant1, rating=4, comment="Good")
    DonationReview.objects.create(donation_item=item, claimant=claimant2, rating=5, comment="Great")

    assert item.total_reviews == 2
    assert item.average_rating == 4.5


def test_donation_average_rating_zero_when_no_review():
    item = make_donation()
    assert item.total_reviews == 0
    assert item.average_rating == 0


# ---------- Claim and review model tests ----------

def test_claim_save_normalizes_status_lowercase_and_trimmed():
    item = make_donation()
    claimant = make_user(username="claimant3")

    claim = DonationClaim.objects.create(
        donation_item=item,
        claimant=claimant,
        message="I need this",
        status=" Approved ",
        contact_number="01712345678",
    )

    assert claim.status == "approved"


def test_claim_unique_together_blocks_duplicate_claim_by_same_user():
    item = make_donation()
    claimant = make_user(username="claimant4")

    DonationClaim.objects.create(donation_item=item, claimant=claimant, message="First claim")

    with pytest.raises(IntegrityError):
        DonationClaim.objects.create(donation_item=item, claimant=claimant, message="Duplicate claim")


def test_claim_can_review_only_completed_without_existing_review():
    item = make_donation()
    claimant = make_user(username="claimant5")
    claim = DonationClaim.objects.create(
        donation_item=item,
        claimant=claimant,
        message="Need this",
        status="completed",
    )

    assert claim.can_review is True

    DonationReview.objects.create(
        donation_item=item,
        claimant=claimant,
        claim=claim,
        rating=5,
        comment="Excellent",
    )

    assert claim.can_review is False


def test_review_model_rejects_rating_outside_one_to_five_when_full_clean_called():
    item = make_donation()
    claimant = make_user(username="claimant6")
    review = DonationReview(donation_item=item, claimant=claimant, rating=6)

    with pytest.raises(ValidationError):
        review.full_clean()


# ---------- Request / donation-to-request / notification tests ----------

def test_request_item_str():
    requester = make_user(username="requester1")
    request_item = make_request(title="Need School Bag", requester=requester)
    assert str(request_item) == "Need School Bag by requester1"


def test_donation_to_request_str_and_default_status():
    donor = make_user(username="donor_c")
    requester = make_user(username="requester2")
    request_item = make_request(title="Need Rice", requester=requester)

    donation = DonationToRequest.objects.create(
        donor=donor,
        request_item=request_item,
        title="Rice donation",
        description="5kg rice",
        quantity=1,
    )

    assert donation.status == "pending"
    assert str(donation) == "Rice donation to Need Rice by donor_c"


def test_notification_str_shortens_message():
    user = make_user(username="notify_user")
    notification = Notification.objects.create(
        user=user,
        message="This is a long notification message for testing",
        link="/profile/",
    )

    assert str(notification).startswith("Notification for notify_user:")
    assert "This is a long notification" in str(notification)


# ---------- Reward model tests ----------

def test_user_reward_add_points_unlocks_rewards_and_next_reward_progress():
    user = make_user(username="reward_user")
    silver = Reward.objects.create(name="Silver", points_required=50, tier_order=1)
    gold = Reward.objects.create(name="Gold", points_required=100, tier_order=2)
    Reward.objects.create(name="Diamond", points_required=200, tier_order=3)

    user_reward = UserReward.objects.create(user=user, points=0)
    user_reward.add_points(75)

    assert user_reward.points == 75
    assert silver in user_reward.rewards.all()
    assert gold not in user_reward.rewards.all()
    assert user_reward.next_reward().name == "Gold"
    assert user_reward.progress_percentage() == 50


def test_user_reward_progress_is_100_when_all_rewards_completed():
    user = make_user(username="top_reward_user")
    Reward.objects.create(name="Silver", points_required=50, tier_order=1)
    Reward.objects.create(name="Gold", points_required=100, tier_order=2)
    Reward.objects.create(name="Diamond", points_required=200, tier_order=3)

    user_reward = UserReward.objects.create(user=user, points=250)
    user_reward.check_rewards()

    assert user_reward.next_reward() is None
    assert user_reward.progress_percentage() == 100
    assert user_reward.rewards.count() == 3


# ---------- NGO model tests ----------

def test_ngo_profile_str_uses_ngo_name_then_username():
    ngo = make_ngo(username="ngo_profile_test")
    profile = ngo.ngoprofile

    assert str(profile) == "Hope Foundation"

    profile.ngo_name = ""
    profile.save()
    assert str(profile) == "ngo_profile_test"


def test_campaign_str_uses_ngo_profile_name():
    ngo = make_ngo(username="ngo_campaign_test")
    campaign = make_campaign(title="Winter Relief", ngo=ngo)

    assert str(campaign) == "Winter Relief by Hope Foundation"


def test_campaign_update_and_ngo_donation_str():
    donor = make_user(username="campaign_donor")
    campaign = make_campaign(title="Flood Relief", status="approved")

    update = CampaignUpdate.objects.create(
        campaign=campaign,
        title="First Update",
        message="We distributed food.",
    )
    donation = NGODonation.objects.create(
        campaign=campaign,
        donor=donor,
        amount=500,
        payment_status="completed",
        transaction_id="tx_test_001",
    )

    assert str(update) == "First Update (Flood Relief)"
    assert str(donation) == "Donation of 500 to Flood Relief by campaign_donor"
