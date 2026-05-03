from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from django.db.models import Count, Q
from donations.models import (
    User, RequestItem, Category, DonationItem, DonationClaim, DonationReview, Notification, ContactMessage, Reward,
    UserReward
)
from ngos.models import Campaign, NGOProfile, CampaignCategory
from datetime import timedelta
from donations.models import DonationReview
from django.urls import reverse


# ===== Custom Admin Panel Views =====

def admin_only(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != "admin":
            return HttpResponseForbidden("Access Denied!")
        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
@admin_only
def admin_dashboard(request):
    # Basic stats
    total_users = User.objects.count()
    total_ngos = User.objects.filter(user_type="ngo").count()
    total_donations = DonationItem.objects.count()
    total_campaigns = Campaign.objects.count()
    total_claims = DonationClaim.objects.count()

    # Approval counts
    pending_ngos_count = User.objects.filter(user_type='ngo', is_approved=False).count()
    pending_campaigns_count = Campaign.objects.filter(status='pending').count()
    pending_requests_count = RequestItem.objects.filter(status='pending').count()

    # Recent activities
    recent_donations = DonationItem.objects.all().order_by('-created_at')[:5]
    recent_claims = DonationClaim.objects.all().order_by('-created_at')[:5]

    # Statistics for charts
    donations_by_status = DonationItem.objects.values('status').annotate(count=Count('id'))
    claims_by_status = DonationClaim.objects.values('status').annotate(count=Count('id'))

    return render(request, "custom_admin/dashboard.html", {
        "total_users": total_users,
        "total_ngos": total_ngos,
        "total_donations": total_donations,
        "total_campaigns": total_campaigns,
        "total_claims": total_claims,
        "pending_ngos_count": pending_ngos_count,
        "pending_campaigns_count": pending_campaigns_count,
        "pending_requests_count": pending_requests_count,
        "recent_donations": recent_donations,
        "recent_claims": recent_claims,
        "donations_by_status": donations_by_status,
        "claims_by_status": claims_by_status,
    })


