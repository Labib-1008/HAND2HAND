from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from donations.models import User, DonorRecipientProfile
from ngos.models import NGOProfile,Campaign,NGODonation
from django.shortcuts import get_object_or_404

from django.contrib.auth import update_session_auth_hash

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from django.db.models import Q, Avg, Count
from django.utils import timezone
from .models import (
    User, DonorRecipientProfile, Category, DonationItem, 
    DonationImage, DonationClaim, DonationReview, 
    RequestItem,DonationToRequest, Notification, ContactMessage, UserReward
)
from .forms import (
    DonationItemForm, DonationClaimForm, 
    DonationReviewForm,RequestItemForm,DonationToRequestForm, ContactForm
)

from django.core.paginator import Paginator
from django.db.models import Q

from django.urls import reverse
from django.db import transaction





# Create your views here.


from django.shortcuts import render, redirect
from donations.models import DonationItem, DonationClaim, RequestItem
from ngos.models import Campaign

def home(request):
    if request.user.is_authenticated and request.user.user_type == 'admin':
        return redirect('admin_dashboard')  # redirect to admin panel

    # Latest NGO campaigns
    ngo_campaigns = Campaign.objects.filter(status='approved', is_active=True).order_by('-id')[:6]

    # Latest donation items
    donate_items = DonationItem.objects.filter(status='available').order_by('-created_at')[:6]

    # Features (static for now)
    features = [
        {'title': 'Donate', 'icon': 'donations/images/icon-donate.png'},
        {'title': 'NGO', 'icon': 'donations/images/ngo.png'},
        {'title': 'Reward', 'icon': 'donations/images/reward.png'},
        {'title': 'Campaign', 'icon': 'donations/images/campaign.png'},
    ]


    context = {
        'ngo_campaigns': ngo_campaigns,
        'donate_items': donate_items,
        'features': features,
    }

    return render(request, 'donations/home.html', context)





# ===== LOGIN VIEW =====
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # ✅ Check if user is NGO and not approved
            if user.user_type == 'ngo' and not user.is_approved:
                messages.error(request, "Your NGO account is pending admin approval. Please wait for approval.")
                return redirect("home")
            
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                
                # ✅ DIRECT REDIRECT - NO CIRCULAR REDIRECT
                if user.user_type == "admin":
                    return redirect("admin_dashboard")
                else:
                    return redirect("home")
            else:
                messages.error(request, "Your account is inactive. Please wait for admin approval.")
        else:
            messages.error(request, "Invalid username or password.")
    
    # ✅ REDIRECT BACK TO HOME WHERE MODAL EXISTS
    return redirect("home")

# ===== LOGOUT VIEW =====
def logout_view(request):
    logout(request)
    return redirect("home")


# ===== SIGNUP VIEW =====

def signup(request):
    if request.method == "POST":
        try:
            print("✅ Signup view called")
            print("📦 POST data:", dict(request.POST))
            print("📁 FILES data:", dict(request.FILES))
            
            user_type = request.POST.get("user_type")
            username = request.POST.get("username")
            email = request.POST.get("email")
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            
            print(f"🔍 User type: {user_type}, Username: {username}")
            
            if not user_type:
                messages.error(request, "Please select a user type.")
                return redirect("home")
                
            if not username or not email:
                messages.error(request, "Username and email are required.")
                return redirect("home")
                
            if password1 != password2:
                messages.error(request, "Passwords do not match.")
                return redirect("home")
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect("home")
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                user_type=user_type
            )
            print("✅ User created successfully")
            
            if user_type == "donor/recipient":
                print("🔄 Creating donor profile")
                DonorRecipientProfile.objects.create(
                    user=user,
                    full_name=request.POST.get("full_name"),
                    email=email,
                    nid_birth_certificate=request.FILES.get("nid_birth_certificate"),
                    city_postal=request.POST.get("city_postal"),
                    address=request.POST.get("address"),
                    mobile_number=request.POST.get("mobile_number"),
                )
                print("✅ Donor profile created")
                
                login(request, user)
                messages.success(request, f"Welcome, {request.POST.get('full_name')}!")
                return redirect("home")
            
            elif user_type == "ngo":
                print("🔄 Creating NGO profile")
                NGOProfile.objects.create(
                    user=user,
                    ngo_name=request.POST.get("ngo_name"),
                    reg_certificate=request.FILES.get("reg_certificate"),
                    email=email,
                    contact_person=request.POST.get("contact_person"),
                    nid_birth_certificate=request.FILES.get("nid_birth_certificate"),
                    city_postal=request.POST.get("city_postal"),
                    address=request.POST.get("address"),
                    ngo_type=request.POST.get("ngo_type"),
                    social_link=request.POST.get("social_link"),
                    mobile_number=request.POST.get("mobile_number"),
                )
                print("✅ NGO profile created")
                
                messages.success(request, "Your NGO registration is submitted. Wait for admin approval.")
                return redirect("home")
                
        except Exception as e:
            import traceback
            print("❌ Error:", traceback.format_exc())
            messages.error(request, f"An error occurred: {str(e)}")
            if 'user' in locals():
                user.delete()
            return redirect("home")
    
    return redirect("home")




def about(request):
    return render(request, "donations/about.html")




def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )
            messages.success(request, "Your message has been received!")
            form = ContactForm()
    else:
        form = ContactForm()
    return render(request, 'donations/contact.html', {'form': form})

@login_required
def my_rewards(request):
    user_reward, created = UserReward.objects.get_or_create(user=request.user)
    next_reward = user_reward.next_reward()
    progress = user_reward.progress_percentage()
    return render(request, "donations/my_rewards.html", {
        "user_reward": user_reward,
        "next_reward": next_reward,
        "progress": progress
    })











# ===== EXPLORE DONATIONS VIEW =====

def explore_donations(request):
    # Show available donations with filtering and search
    donations = DonationItem.objects.filter(status='available').select_related('category', 'donor')
    
    # Get filter parameters
    category_id = request.GET.get('category')
    location = request.GET.get('location')
    urgency = request.GET.get('urgency')
    search_query = request.GET.get('q')
    
    # Apply filters
    if category_id:
        donations = donations.filter(category_id=category_id)
    
    if location:
        donations = donations.filter(location__icontains=location)
    
    if urgency:
        donations = donations.filter(urgency=urgency)
    
    if search_query:
        donations = donations.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Get unique locations for filter dropdown
    locations = DonationItem.objects.filter(status='available').values_list('location', flat=True).distinct()
    
    # Pagination - Add this for better performance with many donations
    paginator = Paginator(donations, 12)  # Show 12 donations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'donations': page_obj,  # Use paginated object
        'categories': categories,
        'locations': [loc for loc in locations if loc],  # Filter out empty values
        'selected_category': category_id,
        'selected_location': location,
        'selected_urgency': urgency,
        'search_query': search_query or '',
    }
    return render(request, "donations/explore_donations.html", context)

# ===== DONATION DETAIL VIEW =====
def donation_detail(request, item_id):
    donation_item = get_object_or_404(DonationItem, id=item_id)
    
    # Check if user can review this item
    can_review = False
    if request.user.is_authenticated:
        completed_claim = DonationClaim.objects.filter(
            donation_item=donation_item,
            claimant=request.user,
            status='completed'
        ).first()
        can_review = completed_claim and not DonationReview.objects.filter(
            donation_item=donation_item,
            claimant=request.user
        ).exists()
    
    #  reviews with user info
    reviews = DonationReview.objects.filter(
    donation_item=donation_item
).select_related('claimant')

    
    context = {
        'donation_item': donation_item,
        'reviews': reviews,
        'can_review': can_review,
        'average_rating': donation_item.average_rating,
        'total_reviews': donation_item.total_reviews,
    }
    return render(request, 'donations/donation_detail.html', context)

# ===== DONATE ITEM VIEW  =====

@login_required
def donate_item(request):
    if request.method == "POST":
        form = DonationItemForm(request.POST, request.FILES)
        if form.is_valid():
            donation_item = form.save(commit=False)
            donation_item.donor = request.user
            donation_item.save()

            # Save single image
            image = form.cleaned_data.get('image')
            if image:
                DonationImage.objects.create(donation_item=donation_item, image=image)

            messages.success(request, "Your donation item has been posted successfully!")
            # add points to user
            user_reward, created = UserReward.objects.get_or_create(user=request.user)
            user_reward.add_points(10)  # 10 points for item donation
            return redirect("explore_donations")
            
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DonationItemForm()

    categories = Category.objects.all()
    return render(request, "donations/donate_item.html", {'form': form, 'categories': categories})



# ===== CLAIM DONATION VIEW =====
@login_required
def claim_donation(request, item_id):
    donation_item = get_object_or_404(DonationItem, id=item_id, status='available')

    # নিজের donation claim করা যাবে না
    if donation_item.donor == request.user:
        messages.error(request, "You cannot claim your own donation.")
        return redirect('donation_detail', item_id=item_id)

    # চেক করব user আগেই claim করেছে কিনা
    if DonationClaim.objects.filter(donation_item=donation_item, claimant=request.user).exists():
        messages.warning(request, "You already claimed this item.")
        return redirect('donation_detail', item_id=item_id)

    if request.method == 'POST':
        form = DonationClaimForm(request.POST)
        if form.is_valid():
            try:
                claim = form.save(commit=False)
                claim.donation_item = donation_item
                claim.claimant = request.user
                claim.save()

                # Update donation status
                donation_item.status = 'reserved'
                donation_item.save()

                
                Notification.objects.create(
                    user=donation_item.donor,
                    message=f"Your donation '{donation_item.title}' has been claimed by {request.user.username}",
                    link=f"/donation/{donation_item.id}/"
                    )

                messages.success(request, "Your claim has been submitted successfully!")
                return redirect('donation_detail', item_id=donation_item.id)

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect('donation_detail', item_id=donation_item.id)
    else:
        form = DonationClaimForm()

    context = {
        'donation_item': donation_item,
        'form': form,
    }
    return render(request, 'donations/claim_donation.html', context)


# ===== SUBMIT REVIEW VIEW =====
@login_required
def submit_review(request, claim_id):
    claim = get_object_or_404(DonationClaim, id=claim_id, claimant=request.user)

    # শুধু completed claim review করা যাবে
    if claim.status != "completed":
        messages.error(request, "You can only review after the donation is completed.")
        return redirect('donation_detail', item_id=claim.donation_item.id)

    # একই user এক donation item এ একবার review দিতে পারবে
    if DonationReview.objects.filter(donation_item=claim.donation_item, claimant=request.user).exists():
        messages.error(request, "You have already reviewed this donation.")
        return redirect('donation_detail', item_id=claim.donation_item.id)

    if request.method == 'POST':
        form = DonationReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.donation_item = claim.donation_item
            review.claimant = request.user
            review.claim = claim
            review.save()

            # ✅ Notify donor
            Notification.objects.create(
                user=claim.donation_item.donor,
                message=f"📣 {request.user.username} submitted a review for '{claim.donation_item.title}'.",
                link=reverse('donation_detail', args=[claim.donation_item.id])
            )

            messages.success(request, "✅ Thank you for your review!")
            return redirect('donation_detail', item_id=claim.donation_item.id)
    else:
        form = DonationReviewForm()

    context = {
        'form': form,
        'claim': claim,
        'donation_item': claim.donation_item,
    }
    return render(request, 'donations/submit_review.html', context)



@login_required
def request_item(request):
    if request.method == "POST":
        form = RequestItemForm(request.POST, request.FILES)
        if form.is_valid():
            donation_request = form.save(commit=False)
            donation_request.requester = request.user
            donation_request.save()
            messages.success(request, "Your donation request has been submitted for approval!")
            return redirect("home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RequestItemForm()
    
    return render(request, "donations/request_item.html", {"form": form})




def donate_to_requests(request):
    """
    Show all approved requests from other users that the logged-in user can fulfill.
    Supports filtering by category, location, search, and urgency.
    """
    # Base queryset: approved requests 
    requests_list = RequestItem.objects.filter(status='approved')

    # Exclude requests that already have donations
    requests_list = requests_list.exclude(donations__isnull=False)

    
    # Get filter values from GET parameters
    category_id = request.GET.get('category')
    location = request.GET.get('location')
    search = request.GET.get('search')
    urgency = request.GET.get('urgency')
    
    # Apply filters
    if category_id:
        requests_list = requests_list.filter(category_id=category_id)
    if location:
        requests_list = requests_list.filter(delivery_location__icontains=location)
    if search:
        requests_list = requests_list.filter(title__icontains=search)
    if urgency:
        requests_list = requests_list.filter(urgency=urgency)
    
    # Get all categories for sidebar filter
    categories = Category.objects.all()
    
    context = {
        "requests_list": requests_list,
        "categories": categories,
        "selected_category": category_id or "",
        "location": location or "",
        "search": search or "",
        "urgency": urgency or "",
    }
    
    return render(request, "donations/donate_to_requests.html", context)


@login_required
def donate_item_to_request(request, request_id):
    request_item = get_object_or_404(RequestItem, id=request_id)

    # Donor cannot donate to own request
    if request_item.requester == request.user:
        messages.error(request, "You cannot donate to your own request.")
        return redirect('donate_to_requests')  # 🔥 ঠিক করা হয়েছে

    if request.method == 'POST':
        form = DonationToRequestForm(request.POST, request.FILES)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.request_item = request_item
            donation.save()


            # add points to user
            user_reward, created = UserReward.objects.get_or_create(user=request.user)
            user_reward.add_points(20)  # 20 points for item donation to request

            # Notification to requester
            Notification.objects.create(
                user=request_item.requester,
                message=f"{request.user.username} has donated '{donation.title}' for your request '{request_item.title}'.",
                link=reverse('request_detail', args=[request_item.id]) 
            )

            messages.success(request, f"Successfully donated '{donation.title}' to {request_item.title}!")
            return redirect('my_donations')  # ✅ donor's my donations page
    else:
        form = DonationToRequestForm()

    context = {
        'form': form,
        'request_item': request_item,
    }
    return render(request, 'donations/donate_item_to_request.html', context)



@login_required
def mark_received(request, donation_id):
    donation = get_object_or_404(DonationToRequest, id=donation_id)
    
    if request.user != donation.request_item.requester:
        messages.error(request, "You are not authorized to confirm this donation.")
        return redirect('request_detail', donation.request_item.id)
    
    if donation.status != 'pending':
        messages.warning(request, "This donation is already marked as received or cancelled.")
        return redirect('request_detail', donation.request_item.id)
    
    # Update status
    donation.status = 'completed'
    donation.save()

    # ✅ Site notification for donor
    Notification.objects.create(
        user=donation.donor,  # <-- ensure it matches your Notification model field
        message=f"Your donation '{donation.title}' to '{donation.request_item.title}' has been received by the requester.",
        link=reverse('request_detail', args=[donation.request_item.id])  # <-- consistent with earlier notifications
    )

    messages.success(request, "Donation marked as received!")
    return redirect('request_detail', donation.request_item.id)




# ===== MY REQUESTS VIEW =====
@login_required
def my_requests(request):
    requests_list = RequestItem.objects.filter(requester=request.user)
    
    context = {
        "requests_list": requests_list
    }
    return render(request, "donations/my_requests.html", context)


@login_required
def edit_request(request, pk):
    req = get_object_or_404(RequestItem, pk=pk, requester=request.user)

    if request.method == "POST":
        form = RequestItemForm(request.POST, request.FILES, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, "Your request has been updated successfully!")
            return redirect("my_requests")
    else:
        form = RequestItemForm(instance=req)

    return render(request, "donations/request_item.html", {"form": form, "is_edit": True})

@login_required
def delete_request(request, pk):
    req = get_object_or_404(RequestItem, pk=pk, requester=request.user)
    req.delete()
    messages.success(request, "Your request has been deleted successfully!")
    return redirect("my_requests")


def request_detail(request, pk):
    req = get_object_or_404(RequestItem, pk=pk)

    donor_has_donated = False
    if request.user.is_authenticated:
        donor_has_donated = req.donations.filter(donor=request.user).exists()

    has_donations = req.donations.exists()

    return render(request, "donations/request_detail.html", {
        "req": req,
        "donor_has_donated": donor_has_donated,
        "has_donations": has_donations,
    })








# ===== MY DONATIONS VIEW =====
@login_required
def my_donations(request):
    # Normal donated items
    donated_items = DonationItem.objects.filter(donor=request.user).order_by('-created_at')
    
    # Donations to requests
    donated_to_requests = DonationToRequest.objects.filter(donor=request.user).order_by('-created_at')
    
    # Donations to NGO campaigns
    donated_to_campaigns = NGODonation.objects.filter(donor=request.user).order_by('-donated_at')
    
    # Claims made by the current user
    claims = DonationClaim.objects.filter(claimant=request.user).order_by('-created_at')
    
    context = {
        'donated_items': donated_items,
        'donated_to_requests': donated_to_requests,
        'donated_to_campaigns': donated_to_campaigns,
        'claims': claims,
    }
    return render(request, 'donations/my_donations.html', context)


# ===== PROFILE VIEW =====
@login_required
def profile(request):
    user = request.user
    
    # Check user type and get appropriate profile
    if user.user_type == 'donor/recipient':
        profile = get_object_or_404(DonorRecipientProfile, user=user)
        context = {
            'profile': profile,
            'user_type': 'donor/recipient'
        }
        return render(request, 'donations/profile.html', context)
    
    elif user.user_type == 'ngo':
        profile = get_object_or_404(NGOProfile, user=user)
        context = {
            'profile': profile,
            'user_type': 'ngo'
        }
        return render(request, 'donations/profile.html', context)
    






@login_required
def update_profile(request):
    if request.method == "POST":
        try:
            user = request.user
            if user.user_type == 'donor/recipient':
                profile = get_object_or_404(DonorRecipientProfile, user=user)
                profile.full_name = request.POST.get('full_name')
                profile.mobile_number = request.POST.get('mobile_number')
            elif user.user_type == 'ngo':
                profile = get_object_or_404(NGOProfile, user=user)
                profile.ngo_name = request.POST.get('ngo_name')
                profile.contact_person = request.POST.get('contact_person')
                profile.ngo_type = request.POST.get('ngo_type')
                profile.social_link = request.POST.get('social_link')
                profile.mobile_number = request.POST.get('mobile_number')
            
            profile.address = request.POST.get('address')
            profile.city_postal = request.POST.get('city_postal')
            profile.save()
            
            messages.success(request, "Profile updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
    
    return redirect('profile')

@login_required
def change_password(request):
    if request.method == "POST":
        user = request.user
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
        elif new_password1 != new_password2:
            messages.error(request, "New passwords don't match.")
        else:
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully!")
    
    return redirect('profile')


@csrf_exempt
@login_required
def upload_photo(request):
    if request.method == "POST" and request.FILES.get('profile_picture'):
        try:
            user = request.user
            user.profile_picture = request.FILES['profile_picture']
            user.save()
            
            # ✅ শুধু success message দিন, URL না দিয়ে
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Profile photo updated successfully!'
                    # ❌ photo_url: user.profile_picture.url - remove this line
                })
            else:
                messages.success(request, "Profile photo updated successfully!")
                
        except Exception as e:
            error_msg = f"Error uploading photo: {str(e)}"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_msg})
            else:
                messages.error(request, error_msg)
    
    return redirect('profile')





# ===== Edit Donation =====

@login_required
def edit_donation(request, item_id):
    donation = get_object_or_404(DonationItem, id=item_id, donor=request.user)
    existing_image = donation.images.first()  # get the first image

    if request.method == "POST":
        form = DonationItemForm(request.POST, instance=donation)
        new_image = request.FILES.get('image')  # single image upload

        if form.is_valid():
            form.save()

            if new_image:
                if existing_image:
                    # Replace old image
                    existing_image.image = new_image
                    existing_image.save()
                else:
                    # Create new image if none existed
                    DonationImage.objects.create(donation_item=donation, image=new_image)

            messages.success(request, "Donation updated successfully!")
            return redirect('my_donations')

    else:
        form = DonationItemForm(instance=donation)

    context = {
        'form': form,
        'donation': donation,
        'existing_image': existing_image
    }
    return render(request, 'donations/edit_donation.html', context)


# ===== delete Donation =====
@login_required
def delete_donation(request, item_id):
    item = get_object_or_404(DonationItem, id=item_id, donor=request.user)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Donation deleted successfully!")
        return redirect('my_donations')
    
    # Show a confirmation page
    return render(request, 'donations/confirm_delete.html', {'item': item})







# ===== Approve / Reject Claim =====
@login_required
def handle_claim(request, claim_id, action):
    claim = get_object_or_404(DonationClaim, id=claim_id, donation_item__donor=request.user)
    donation_item = claim.donation_item

    if action not in ['approve', 'reject']:
        messages.error(request, "Invalid action.")
        return redirect('donation_detail', item_id=donation_item.id)

    with transaction.atomic():
        if action == 'approve' and claim.status == 'pending':
            claim.status = 'approved'
            donation_item.status = 'claimed'
            Notification.objects.create(
                user=claim.claimant,
                message=f"✅ Your claim for '{donation_item.title}' has been approved.",
                link=reverse('donation_detail', args=[donation_item.id])
            )

        elif action == 'reject' and claim.status == 'pending':
            claim.status = 'rejected'
            donation_item.status = 'available'
            Notification.objects.create(
                user=claim.claimant,
                message=f"❌ Your claim for '{donation_item.title}' has been rejected.",
                link=reverse('donation_detail', args=[donation_item.id])
            )
        else:
            messages.error(request, f"Action '{action}' cannot be performed on this claim.")
            return redirect('donation_detail', item_id=donation_item.id)

        claim.save()
        donation_item.save()

    messages.success(request, f"Claim has been {action}.")
    return redirect('donation_detail', item_id=donation_item.id)

# ===== Mark Claim as Completed =====
from django.db import transaction

@login_required
def complete_claim(request, claim_id):
    """
    Donor marks an approved claim as completed.
    """
    claim = get_object_or_404(DonationClaim, id=claim_id)
    donation_item = claim.donation_item

    # Only the donor who owns the donation can mark it complete
    if donation_item.donor != request.user:
        messages.error(request, "You are not authorized to complete this claim.")
        return redirect('donation_detail', item_id=donation_item.id)

    # Make status check robust
    current_status = claim.status.lower().strip()
    if current_status != 'approved':
        messages.error(request, "Only approved claims can be marked as completed.")
        return redirect('donation_detail', item_id=donation_item.id)

    # ✅ Wrap updates in a transaction for safety
    with transaction.atomic():
        claim.status = 'completed'
        donation_item.status = 'claimed'  # still reserved/claimed
        claim.save()
        donation_item.save()

        # Notify claimant
        Notification.objects.create(
            user=claim.claimant,
            message=f"📦 Donation '{donation_item.title}' has been marked as completed by {request.user.username}. You can now submit a review.",
            link=reverse('donation_detail', args=[donation_item.id])
        )

    messages.success(request, "Claim has been marked as completed.")
    return redirect('donation_detail', item_id=donation_item.id)





@login_required
def my_claims(request):
    claims = DonationClaim.objects.filter(claimant=request.user)
    return render(request, 'donations/my_claims.html', {'claims': claims})




# ===== Notifications Page =====

@login_required
def notifications_page(request):
    # সব notification
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # সব unread notification mark as read
    notifications.filter(is_read=False).update(is_read=True)

    context = {
        'notifications': notifications,
        'notifications_unread_count': 0,  # সব read হয়ে গিয়েছে
    }
    return render(request, 'donations/notifications.html', context)





