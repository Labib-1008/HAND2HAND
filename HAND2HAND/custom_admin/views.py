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


# Base admin context processor (optional)
def admin_context(request):
    if request.user.is_authenticated and request.user.user_type == 'admin':
        return {
            'pending_ngos_count': User.objects.filter(user_type='ngo', is_approved=False).count(),
            'pending_campaigns_count': Campaign.objects.filter(status='pending').count(),
            'pending_requests_count': RequestItem.objects.filter(status='pending').count(),
        }
    return {}


@login_required
@admin_only
def manage_users(request):
    users = User.objects.exclude(user_type="admin")
    return render(request, "custom_admin/manage_users.html", {"users": users})


@login_required
@admin_only
def manage_ngos(request):
    ngos = User.objects.filter(user_type="ngo")
    return render(request, "custom_admin/manage_ngos.html", {"ngos": ngos})


@login_required
@admin_only
def manage_donations(request):
    # Show both old and new donation systems
    old_donations = DonationItem.objects.all()
    new_donations = DonationItem.objects.all()

    return render(request, "custom_admin/manage_donations.html", {
        "old_donations": old_donations,
        "new_donations": new_donations
    })


@login_required
@admin_only
def manage_donation_claims(request):
    claims = DonationClaim.objects.all().select_related('donation_item', 'claimant')
    return render(request, "custom_admin/manage_donation_claims.html", {"claims": claims})


@login_required
@admin_only
def manage_campaigns(request):
    campaigns = Campaign.objects.all()
    return render(request, "custom_admin/manage_campaigns.html", {"campaigns": campaigns})


@login_required
@admin_only
def manage_categories(request):
    categories = Category.objects.all().annotate(
        donation_count=Count('donationitem')
    )
    return render(request, "custom_admin/manage_categories.html", {"categories": categories})


@login_required
@admin_only
def manage_admins(request):
    admins = User.objects.filter(user_type="admin")
    return render(request, "custom_admin/manage_admins.html", {"admins": admins})


@login_required
@admin_only
def manage_reviews(request):
    reviews = DonationReview.objects.all().select_related('donation_item', 'claimant')
    return render(request, "custom_admin/manage_reviews.html", {"reviews": reviews})


def redirect_after_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == "admin":
            return redirect("admin_dashboard")  # ✅ custom admin panel
        else:
            return redirect("home")  # normal user dashboard/home
    return redirect("login")


@login_required
@admin_only
def admin_profile(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "profile_info":
            # Handle profile information update
            user = request.user
            name = request.POST.get("name")
            email = request.POST.get("email")

            user.username = name
            user.email = email
            user.save()

            messages.success(request, "Profile updated successfully ✅")
            return redirect("admin_profile")

        elif form_type == "password_change":
            # Handle password change
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                # Keep the user logged in after password change
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully ✅")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Password error: {error}")

            return redirect("admin_profile")

    # For GET requests, just render the profile page
    return render(request, "custom_admin/admin_profile.html")


# ===== APPROVAL SYSTEM VIEWS =====

@login_required
@admin_only
def ngo_approval_list(request):
    pending_ngos = User.objects.filter(user_type='ngo', is_approved=False)
    return render(request, 'custom_admin/ngo_approval_list.html', {
        'pending_ngos': pending_ngos
    })


@login_required
@admin_only
def approve_ngo(request, user_id):
    ngo_user = get_object_or_404(User, id=user_id, user_type='ngo')
    ngo_user.is_approved = True
    ngo_user.save()

    # Create notification for NGO
    Notification.objects.create(
        user=ngo_user,
        message="Your NGO account has been approved! You can now access all features.",
        link="/profile/"
    )

    messages.success(request, f'NGO {ngo_user.username} has been approved!')
    return redirect('ngo_approval_list')


@login_required
@admin_only
def reject_ngo(request, user_id):
    ngo_user = get_object_or_404(User, id=user_id, user_type='ngo')
    ngo_user.delete()
    messages.success(request, f'NGO {ngo_user.username} has been rejected and removed!')
    return redirect('ngo_approval_list')


@login_required
@admin_only
def campaign_approval_list(request):
    pending_campaigns = Campaign.objects.filter(status='pending')
    return render(request, 'custom_admin/campaign_approval_list.html', {
        'pending_campaigns': pending_campaigns
    })


@login_required
@admin_only
def approve_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    campaign.status = 'approved'
    campaign.approved_at = timezone.now()
    campaign.save()

    # Create notification for NGO
    Notification.objects.create(
        user=campaign.ngo,
        message=f"Your campaign '{campaign.title}' has been approved!",
        link=f"/campaigns/{campaign.id}/"
    )

    messages.success(request, f'Campaign "{campaign.title}" has been approved!')
    return redirect('campaign_approval_list')


@login_required
@admin_only
def reject_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    campaign.status = 'rejected'
    campaign.save()

    Notification.objects.create(
        user=campaign.ngo,
        message=f"Your campaign '{campaign.title}' has been rejected. Please contact admin for details.",
        link=reverse('my_campaigns')

    )

    messages.success(request, f'Campaign "{campaign.title}" has been rejected!')
    return redirect('campaign_approval_list')


@login_required
@admin_only
def donation_request_approval_list(request):
    pending_requests = RequestItem.objects.filter(status='pending')
    return render(request, 'custom_admin/donation_request_approval_list.html', {
        'pending_requests': pending_requests
    })


@login_required
@admin_only
def approve_donation_request(request, request_id):
    donation_request = get_object_or_404(RequestItem, id=request_id)
    donation_request.status = 'approved'
    donation_request.approved_at = timezone.now()
    donation_request.save()

    # Correct link to request_detail page
    detail_link = reverse('request_detail', kwargs={'pk': donation_request.pk})

    Notification.objects.create(
        user=donation_request.requester,
        message=f"Your donation request '{donation_request.title}' has been approved!",
        link=detail_link
    )

    messages.success(request, f'Donation request "{donation_request.title}" has been approved!')
    return redirect('donation_request_approval_list')


@login_required
@admin_only
def reject_donation_request(request, request_id):
    donation_request = get_object_or_404(RequestItem, id=request_id)
    donation_request.status = 'rejected'
    donation_request.save()

    # Correct link to my_requests page
    detail_link = reverse('request_detail', kwargs={'pk': donation_request.pk})

    Notification.objects.create(
        user=donation_request.requester,
        message=f"Your donation request '{donation_request.title}' has been rejected. Please contact admin for details.",
        link=detail_link
    )

    messages.success(request, f'Donation request "{donation_request.title}" has been rejected!')
    return redirect('donation_request_approval_list')

