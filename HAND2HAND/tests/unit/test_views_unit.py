from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from donations.models import (
    User,
    Category,
    DonationItem,
    DonationClaim,
    DonationReview,
    RequestItem,
    DonationToRequest,
    Notification,
    UserReward,
)
from ngos.models import NGOProfile, Campaign, CampaignCategory


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
    return Category.objects.create(name=name, description=f"{name} items")


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


# ---------- Admin approval unit/integration tests ----------

def test_admin_can_approve_ngo_and_notification_created(client):
    admin = make_admin()
    ngo = make_ngo(username="pending_ngo_view", approved=False)
    client.force_login(admin)

    response = client.get(reverse("approve_ngo", args=[ngo.id]))

    ngo.refresh_from_db()
    assert response.status_code == 302
    assert ngo.is_approved is True
    assert Notification.objects.filter(user=ngo, message__icontains="approved").exists()


def test_non_admin_cannot_access_admin_dashboard(client):
    normal_user = make_user(username="normal_view_user")
    client.force_login(normal_user)

    response = client.get(reverse("admin_dashboard"))

    assert response.status_code == 403


def test_admin_can_approve_campaign_and_notification_created(client):
    admin = make_admin()
    ngo = make_ngo(username="ngo_campaign_view", approved=True)
    campaign = make_campaign(title="Health Support", ngo=ngo, status="pending")
    client.force_login(admin)

    response = client.get(reverse("approve_campaign", args=[campaign.id]))

    campaign.refresh_from_db()
    assert response.status_code == 302
    assert campaign.status == "approved"
    assert campaign.approved_at is not None
    assert Notification.objects.filter(user=ngo, message__icontains="approved").exists()


def test_admin_can_reject_campaign_and_notification_created(client):
    admin = make_admin()
    ngo = make_ngo(username="ngo_reject_view", approved=True)
    campaign = make_campaign(title="Reject Me", ngo=ngo, status="pending")
    client.force_login(admin)

    response = client.get(reverse("reject_campaign", args=[campaign.id]))

    campaign.refresh_from_db()
    assert response.status_code == 302
    assert campaign.status == "rejected"
    assert Notification.objects.filter(user=ngo, message__icontains="rejected").exists()


def test_admin_can_approve_donation_request_and_notification_created(client):
    admin = make_admin()
    requester = make_user(username="requester_view")
    request_item = make_request(title="Need Notebook", requester=requester, status="pending")
    client.force_login(admin)

    response = client.get(reverse("approve_donation_request", args=[request_item.id]))

    request_item.refresh_from_db()
    assert response.status_code == 302
    assert request_item.status == "approved"
    assert request_item.approved_at is not None
    assert Notification.objects.filter(user=requester, message__icontains="approved").exists()


def test_admin_can_reject_donation_request_and_notification_created(client):
    admin = make_admin()
    requester = make_user(username="requester_reject_view")
    request_item = make_request(title="Need Medicine", requester=requester, status="pending")
    client.force_login(admin)

    response = client.get(reverse("reject_donation_request", args=[request_item.id]))

    request_item.refresh_from_db()
    assert response.status_code == 302
    assert request_item.status == "rejected"
    assert Notification.objects.filter(user=requester, message__icontains="rejected").exists()


# ---------- Donor/recipient flow view tests ----------

def test_claim_donation_creates_claim_updates_status_and_notifies_donor(client):
    donor = make_user(username="donor_claim_view")
    claimant = make_user(username="claimant_view")
    item = make_donation(title="Claimable Item", donor=donor, status="available")
    client.force_login(claimant)

    preferred_date = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
    response = client.post(
        reverse("claim_donation", args=[item.id]),
        data={
            "message": "I need this donation.",
            "preferred_date": preferred_date,
            "contact_number": "01712345678",
        },
    )

    item.refresh_from_db()
    assert response.status_code == 302
    assert item.status == "reserved"
    assert DonationClaim.objects.filter(donation_item=item, claimant=claimant).exists()
    assert Notification.objects.filter(user=donor, message__icontains="claimed").exists()


def test_user_cannot_claim_own_donation(client):
    donor = make_user(username="own_donor_view")
    item = make_donation(title="Own Item", donor=donor, status="available")
    client.force_login(donor)

    response = client.post(
        reverse("claim_donation", args=[item.id]),
        data={
            "message": "Trying own claim.",
            "contact_number": "01712345678",
        },
    )

    item.refresh_from_db()
    assert response.status_code == 302
    assert item.status == "available"
    assert DonationClaim.objects.filter(donation_item=item, claimant=donor).exists() is False


def test_donor_can_approve_claim_and_notification_created(client):
    donor = make_user(username="donor_approve_claim")
    claimant = make_user(username="claimant_approve_claim")
    item = make_donation(title="Approve Claim Item", donor=donor, status="reserved")
    claim = DonationClaim.objects.create(
        donation_item=item,
        claimant=claimant,
        message="Need this",
        status="pending",
    )
    client.force_login(donor)

    response = client.get(reverse("handle_claim", args=[claim.id, "approve"]))

    claim.refresh_from_db()
    item.refresh_from_db()
    assert response.status_code == 302
    assert claim.status == "approved"
    assert item.status == "claimed"
    assert Notification.objects.filter(user=claimant, message__icontains="approved").exists()


def test_only_donation_owner_can_approve_claim(client):
    donor = make_user(username="real_donor")
    other_user = make_user(username="wrong_donor")
    claimant = make_user(username="claimant_wrong_owner")
    item = make_donation(title="Protected Claim Item", donor=donor, status="reserved")
    claim = DonationClaim.objects.create(
        donation_item=item,
        claimant=claimant,
        message="Need this",
        status="pending",
    )
    client.force_login(other_user)

    response = client.get(reverse("handle_claim", args=[claim.id, "approve"]))

    assert response.status_code == 404


def test_donor_can_complete_approved_claim_and_notify_claimant(client):
    donor = make_user(username="donor_complete_claim")
    claimant = make_user(username="claimant_complete_claim")
    item = make_donation(title="Complete Claim Item", donor=donor, status="claimed")
    claim = DonationClaim.objects.create(
        donation_item=item,
        claimant=claimant,
        message="Need this",
        status="approved",
    )
    client.force_login(donor)

    response = client.get(reverse("complete_claim", args=[claim.id]))

    claim.refresh_from_db()
    item.refresh_from_db()
    assert response.status_code == 302
    assert claim.status == "completed"
    assert item.status == "claimed"
    assert Notification.objects.filter(user=claimant, message__icontains="completed").exists()


def test_claimant_can_submit_review_after_completed_claim(client):
    donor = make_user(username="donor_review_view")
    claimant = make_user(username="claimant_review_view")
    item = make_donation(title="Review Item", donor=donor, status="claimed")
    claim = DonationClaim.objects.create(
        donation_item=item,
        claimant=claimant,
        message="Need this",
        status="completed",
    )
    client.force_login(claimant)

    response = client.post(
        reverse("submit_review", args=[claim.id]),
        data={"rating": 5, "comment": "Great donation."},
    )

    assert response.status_code == 302
    assert DonationReview.objects.filter(donation_item=item, claimant=claimant, rating=5).exists()
    assert Notification.objects.filter(user=donor, message__icontains="submitted a review").exists()


def test_requester_can_mark_donation_to_request_as_received(client):
    donor = make_user(username="donor_mark_received")
    requester = make_user(username="requester_mark_received")
    request_item = make_request(title="Need Food", requester=requester, status="approved")
    donation = DonationToRequest.objects.create(
        donor=donor,
        request_item=request_item,
        title="Food Pack",
        description="Food donation",
        quantity=1,
        status="pending",
    )
    client.force_login(requester)

    response = client.get(reverse("mark_received", args=[donation.id]))

    donation.refresh_from_db()
    assert response.status_code == 302
    assert donation.status == "completed"
    assert Notification.objects.filter(user=donor, message__icontains="received").exists()


def test_non_requester_cannot_mark_donation_to_request_received(client):
    donor = make_user(username="donor_no_mark")
    requester = make_user(username="requester_no_mark")
    other_user = make_user(username="other_no_mark")
    request_item = make_request(title="Need Clothes", requester=requester, status="approved")
    donation = DonationToRequest.objects.create(
        donor=donor,
        request_item=request_item,
        title="Clothes Pack",
        description="Clothes donation",
        quantity=1,
        status="pending",
    )
    client.force_login(other_user)

    response = client.get(reverse("mark_received", args=[donation.id]))

    donation.refresh_from_db()
    assert response.status_code == 302
    assert donation.status == "pending"


# ---------- NGO campaign view tests ----------

def test_ngo_can_create_campaign_status_pending(client):
    ngo = make_ngo(username="ngo_create_campaign", approved=True)
    category = CampaignCategory.objects.create(name="Healthcare")
    client.force_login(ngo)

    response = client.post(
        reverse("create_campaign"),
        data={
            "title": "Medicine Fund",
            "description": "Need fund for medicine.",
            "goal_amount": "5000.00",
            "end_date": (timezone.now().date() + timedelta(days=30)).isoformat(),
            "category": str(category.id),
        },
    )

    assert response.status_code == 302
    campaign = Campaign.objects.get(title="Medicine Fund")
    assert campaign.ngo == ngo
    assert campaign.status == "pending"
