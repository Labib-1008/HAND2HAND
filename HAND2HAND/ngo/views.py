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


def campaign_detail(request, campaign_id):
    # Get campaign
    campaign = get_object_or_404(
        Campaign.objects.annotate(
            donors_count=Count('donations'),
            total_raised=Sum('donations__amount')
        ),
        id=campaign_id,
        status='approved',
        is_active=True
    )


    # Calculate fundraising progress
    campaign.progress_percent = 0
    if campaign.goal_amount and campaign.goal_amount > 0:
        raised = campaign.collected_amount or 0  
        campaign.progress_percent = round((raised / campaign.goal_amount) * 100, 2)


    # Donations for this campaign
    donations = NGODonation.objects.filter(campaign=campaign).order_by('-donated_at')

    # Updates for this campaign (optional)
    updates = CampaignUpdate.objects.filter(campaign=campaign).order_by('-created_at')

    context = {
        'campaign': campaign,
        'donations': donations,
        'updates': updates,
    }

    return render(request, 'ngos/campaign_detail.html', context)





@login_required
def donate_to_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, status="approved", is_active=True)

    if request.user == campaign.ngo:
        messages.error(request, "⚠️ You cannot donate to your own campaign.")
        return redirect("campaign_detail", campaign_id=campaign.id)

    form = NGODonationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        amount = form.cleaned_data['amount']
        is_anonymous = form.cleaned_data.get('is_anonymous', False)
        payer_name = '' if is_anonymous else form.cleaned_data.get('payer_name', '')
        account_input = '' if is_anonymous else form.cleaned_data.get('account_input', '')
        message = form.cleaned_data.get('message', '')
        tran_id = f"{campaign.id}_{request.user.id}_{uuid.uuid4().hex[:8]}"  # Unique ID
        

        # SSLCommerz request data
        data = {
            "store_id": settings.SSL_COMMERZ_STORE_ID,
            "store_passwd": settings.SSL_COMMERZ_STORE_PASS,
            "total_amount": float(amount),
            "currency": "BDT",
            "tran_id": tran_id,
            "success_url": request.build_absolute_uri(reverse('ssl_success')),
            "fail_url": request.build_absolute_uri(reverse('ssl_fail')),
            "cancel_url": request.build_absolute_uri(reverse('ssl_cancel')),
            "cus_name": request.user.username,
            "cus_email": request.user.email or 'test@test.com',
            "cus_add1": "Dhaka",
            "cus_city": "Dhaka",
            "cus_postcode": "1200",
            "cus_country": "Bangladesh",
            "cus_phone": "01700000000",
            "product_name": campaign.title,
            "product_category": "Donation",
            "product_profile": "non-physical-goods",
            "value_a": str(campaign.id),
            "shipping_method": "NO",
            "value_b": message,  # <-- message passed here
            "value_c": str(is_anonymous),  # <-- pass anonymous flag
        }

        try:
            url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
            response = requests.post(url, data=data, timeout=10)
            res_json = response.json()
            gateway_url = res_json.get("GatewayPageURL")

            if gateway_url:
                return redirect(gateway_url)
            else:
                messages.error(request, "Payment initiation failed. Try again.")
        except Exception as e:
            messages.error(request, f"Payment error: {e}")

    return render(request, "ngos/donate_to_campaign.html", {"campaign": campaign, "form": form})

# ===== Callbacks =====

@csrf_exempt
def ssl_success(request):
    data = request.POST or request.GET
    tran_id = data.get("tran_id")
    status = str(data.get("status", "")).strip().upper()
    amount_str = data.get("amount", "0")
    try:
        amount = Decimal(amount_str)
    except:
        amount = Decimal(0)

    # ✅ Only proceed if status is VALID or SUCCESS
    if status not in ["VALID", "SUCCESS"]:
        return redirect(reverse('donation_error_page') + "?" + urlencode({"msg": f"Payment failed (status={status})"}))

    # Validate tran_id
    try:
        campaign_id, user_id, _ = tran_id.split("_")
    except Exception:
        return redirect(reverse('donation_error_page') + "?" + urlencode({"msg": "Invalid transaction ID format."}))

    campaign = get_object_or_404(Campaign, id=campaign_id)
    User = get_user_model()
    donor = get_object_or_404(User, id=user_id)

    donation_message = data.get("value_b", "")
    is_anonymous = data.get("value_c", "False") == "True"  # convert string to boolean

    # Create donation (success only)
    donation = NGODonation.objects.create(
        campaign=campaign,
        donor=donor,
        amount=amount,
        transaction_id=tran_id,
        payment_method="SSLCommerz",
        payment_status="completed",
        message=donation_message,
        is_anonymous=is_anonymous
    )

    # Reward points
    user_reward, _ = UserReward.objects.get_or_create(user=donor)
    user_reward.add_points(30)

    # Notification to NGO
    Notification.objects.create(
        user=campaign.ngo,
        message=f"{donor.username} donated ৳{amount} to your campaign '{campaign.title}'",
        link=reverse('campaign_detail', args=[campaign.id])
    )

    return redirect('donation_success_page', donation_id=donation.id)


@csrf_exempt
def ssl_fail(request):
    data = request.POST or request.GET
    tran_id = data.get("tran_id")
    amount = data.get("amount", 0)

    # Mark pending donation as failed if exists
    if tran_id:
        NGODonation.objects.filter(transaction_id=tran_id, payment_status="pending") \
                           .update(payment_status="failed")

    msg = f"Payment failed for transaction {tran_id} (Amount: ৳{amount})"
    return redirect(reverse('donation_error_page') + "?" + urlencode({"msg": msg}))


@csrf_exempt
def ssl_cancel(request):
    data = request.POST or request.GET
    tran_id = data.get("tran_id")
    amount = data.get("amount", 0)

    # Mark pending donation as failed if exists
    if tran_id:
        NGODonation.objects.filter(transaction_id=tran_id, payment_status="pending") \
                           .update(payment_status="failed")

    msg = f"Payment cancelled for transaction {tran_id} (Amount: ৳{amount})"
    return redirect(reverse('donation_error_page') + "?" + urlencode({"msg": msg}))


@login_required
def donation_success_page(request, donation_id):
    donation = get_object_or_404(NGODonation, id=donation_id, donor=request.user)
    return render(request, "ngos/donation_success.html", {"donation": donation})

@login_required
def donation_error_page(request):
    msg = request.GET.get("msg", "Payment failed. Please try again.")
    return render(request, "ngos/payment_error.html", {"msg": msg})



@login_required
def download_receipt(request, donation_id):
    donation = get_object_or_404(NGODonation, id=donation_id, donor=request.user)

    template = get_template("ngos/receipt_pdf.html")
    html = template.render({"donation": donation})

    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="receipt_{donation.id}.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=500)




@login_required
def add_campaign_update(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    # Only NGO owner can add updates
    if request.user != campaign.ngo:
        messages.error(request, "You are not authorized to add updates to this campaign.")
        return redirect('campaign_detail', campaign_id=campaign.id)

    if request.method == "POST":
        title = request.POST.get('title')
        message = request.POST.get('message')

        if title and message:
            CampaignUpdate.objects.create(
                campaign=campaign,
                title=title,
                message=message
            )
            messages.success(request, "Update added successfully!")
            return redirect(f"{reverse('campaign_detail', args=[campaign_id])}?tab=updates")
        else:
            messages.error(request, "Both title and message are required.")

    return redirect('campaign_detail', campaign_id=campaign.id)


@login_required
def ngo_donation_history(request):
    # Only allow NGO users
    if request.user.user_type != 'ngo':
        return render(request, '403.html')  # or redirect with message

    # Get all donations to campaigns of this NGO
    donations = NGODonation.objects.filter(campaign__ngo=request.user).order_by('-donated_at')

    context = {
        'donations': donations,
    }
    return render(request, 'ngos/donation_history.html', context)




