from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Campaign, NGODonation
from .forms import CampaignForm, NGODonationForm
from ngos.models import Campaign, CampaignCategory, NGOProfile,NGODonation, CampaignUpdate
from donations.models import User, UserReward
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.utils import timezone
from django.db.models import Q, Count,F

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from .models import NGODonation
from donations.models import Notification
from django.urls import reverse


from decimal import Decimal
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import requests
import uuid
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from urllib.parse import urlencode

@login_required
def create_campaign(request):
    if request.user.user_type != 'ngo':
        messages.error(request, "Only NGOs can create campaigns.")
        return redirect('home')

    if request.method == "POST":
        form = CampaignForm(request.POST, request.FILES)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.ngo = request.user
            campaign.status = 'pending'  # require admin approval
            campaign.save()
            messages.success(request, "Campaign submitted for admin approval.")
            return redirect('my_campaigns')
    else:
        form = CampaignForm()

    return render(request, "ngos/create_campaign.html", {"form": form})

@login_required
def edit_campaign(request, campaign_id):
    if request.user.user_type != 'ngo':
        messages.error(request, "Only NGOs can edit campaigns.")
        return redirect('home')

    campaign = get_object_or_404(Campaign, id=campaign_id, ngo=request.user)

    if request.method == "POST":
        form = CampaignForm(request.POST, request.FILES, instance=campaign)
        if form.is_valid():
            updated_campaign = form.save(commit=False)
            updated_campaign.ngo = request.user  # ensure same ngo
            updated_campaign.status = 'pending'  # আবার approval লাগতে পারে
            updated_campaign.save()
            messages.success(request, "Campaign updated successfully (pending approval).")
            return redirect('my_campaigns')
    else:
        form = CampaignForm(instance=campaign)

    return render(request, "ngos/edit_campaign.html", {"form": form, "campaign": campaign})


@login_required
def delete_campaign(request, campaign_id):
    if request.user.user_type != 'ngo':
        messages.error(request, "Only NGOs can delete campaigns.")
        return redirect('home')

    campaign = get_object_or_404(Campaign, id=campaign_id, ngo=request.user)

    if request.method == "POST":
        campaign.delete()
        messages.success(request, "Campaign deleted successfully.")
        return redirect('my_campaigns')

    return redirect('my_campaigns')




@login_required
def my_campaigns(request):
    if request.user.user_type != 'ngo':
        messages.error(request, "Only NGOs can view their campaigns.")
        return redirect('home')

    campaigns = Campaign.objects.filter(ngo=request.user)
    return render(request, "ngos/my_campaigns.html", {"campaigns": campaigns})








def explore_campaigns(request):
    # Filters
    search_query = request.GET.get('q', '')
    selected_category = request.GET.get('category')
    selected_location = request.GET.get('location')
    selected_ngo = request.GET.get('ngo')

    # Base queryset: only approved, active campaigns that haven't ended yet OR have no end date
    campaigns = Campaign.objects.filter(
        status='approved',
        is_active=True
    ).filter(
        Q(end_date__gte=timezone.now()) | Q(end_date__isnull=True)
    )

    # Apply filters
    if search_query:
        campaigns = campaigns.filter(title__icontains=search_query)
    if selected_category:
        campaigns = campaigns.filter(category__id=selected_category)
    if selected_location:
        campaigns = campaigns.filter(ngo__ngoprofile__city_postal=selected_location)
    if selected_ngo:
        campaigns = campaigns.filter(ngo__id=selected_ngo)

    # Annotate donors count
    campaigns = campaigns.annotate(donors_count=Count('donations'))

    # Order by approved_at descending (latest first) → fixes UnorderedObjectListWarning
    campaigns = campaigns.order_by('-approved_at')

    # Calculate progress percent
    for campaign in campaigns:
        campaign.progress_percent = 0
        if campaign.goal_amount and campaign.goal_amount > 0:
            campaign.progress_percent = (campaign.collected_amount / campaign.goal_amount) * 100

    # Pagination
    paginator = Paginator(campaigns, 9)
    page_number = request.GET.get('page')
    campaigns_page = paginator.get_page(page_number)

    # Dropdown filters
    categories = CampaignCategory.objects.all()
    locations = NGOProfile.objects.values_list('city_postal', flat=True).distinct()
    ngos = NGOProfile.objects.filter(user__is_approved=True)

    context = {
        'campaigns': campaigns_page,
        'categories': categories,
        'locations': locations,
        'ngos': ngos,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_location': selected_location,
        'selected_ngo': selected_ngo,
    }

    return render(request, 'ngos/explore_campaigns.html', context)


##