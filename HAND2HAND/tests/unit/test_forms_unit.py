from datetime import timedelta

import pytest
from django.utils import timezone

from donations.forms import DonationClaimForm, DonationReviewForm, RequestItemForm
from donations.models import Category


pytestmark = pytest.mark.django_db


def test_donation_claim_form_valid_data():
    future_date = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
    form = DonationClaimForm(
        data={
            "message": "I need this item for my family.",
            "preferred_date": future_date,
            "contact_number": "01712345678",
        }
    )

    assert form.is_valid(), form.errors


def test_donation_claim_form_rejects_non_digit_contact_number():
    form = DonationClaimForm(
        data={
            "message": "Need it",
            "contact_number": "01712abc678",
        }
    )

    assert form.is_valid() is False
    assert "contact_number" in form.errors
    assert "only contain digits" in str(form.errors["contact_number"])


def test_donation_claim_form_rejects_short_contact_number():
    form = DonationClaimForm(
        data={
            "message": "Need it",
            "contact_number": "12345",
        }
    )

    assert form.is_valid() is False
    assert "contact_number" in form.errors
    assert "valid phone number" in str(form.errors["contact_number"])


def test_donation_claim_form_rejects_past_preferred_date():
    past_date = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
    form = DonationClaimForm(
        data={
            "message": "Need it",
            "preferred_date": past_date,
            "contact_number": "01712345678",
        }
    )

    assert form.is_valid() is False
    assert "preferred_date" in form.errors
    assert "cannot be in the past" in str(form.errors["preferred_date"])


def test_donation_review_form_valid_rating():
    form = DonationReviewForm(data={"rating": 5, "comment": "Very good donation."})
    assert form.is_valid(), form.errors


def test_donation_review_form_rejects_rating_above_five():
    form = DonationReviewForm(data={"rating": 6, "comment": "Invalid rating."})
    assert form.is_valid() is False
    assert "rating" in form.errors


def test_request_item_form_valid_data():
    category = Category.objects.create(name="Food")
    needed_date = (timezone.now().date() + timedelta(days=2)).isoformat()

    form = RequestItemForm(
        data={
            "title": "Need rice for family",
            "category": str(category.id),
            "quantity": 2,
            "description": "Need food support.",
            "needed_before": needed_date,
            "delivery_location": "Rangpur",
            "contact_number": "01712345678",
            "notify_immediately": "on",
            "urgency": "high",
        }
    )

    assert form.is_valid(), form.errors


def test_request_item_form_rejects_past_needed_before_date():
    category = Category.objects.create(name="Medical")
    past_date = (timezone.now().date() - timedelta(days=1)).isoformat()

    form = RequestItemForm(
        data={
            "title": "Need medicine",
            "category": str(category.id),
            "quantity": 1,
            "description": "Need medicine support.",
            "needed_before": past_date,
            "delivery_location": "Dhaka",
            "contact_number": "01712345678",
            "urgency": "medium",
        }
    )

    assert form.is_valid() is False
    assert "needed_before" in form.errors
    assert "cannot be in the past" in str(form.errors["needed_before"])


def test_request_item_form_rejects_quantity_less_than_one():
    category = Category.objects.create(name="Education")

    form = RequestItemForm(
        data={
            "title": "Need books",
            "category": str(category.id),
            "quantity": 0,
            "description": "Need books.",
            "delivery_location": "Dhaka",
            "contact_number": "01712345678",
            "urgency": "low",
        }
    )

    assert form.is_valid() is False
    assert "quantity" in form.errors
    assert "at least 1" in str(form.errors["quantity"])
