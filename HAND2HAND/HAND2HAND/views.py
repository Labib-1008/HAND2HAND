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
