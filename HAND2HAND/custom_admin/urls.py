from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),
    
    # Management Pages
    path('users/', views.manage_users, name='manage_users'),
    path('ngos/', views.manage_ngos, name='manage_ngos'),
    path('donations/', views.manage_donations, name='manage_donations'),
    path('donation-claims/', views.manage_donation_claims, name='manage_donation_claims'),
    path('campaigns/', views.manage_campaigns, name='manage_campaigns'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('admins/', views.manage_admins, name='manage_admins'),
    path('reviews/', views.manage_reviews, name='manage_reviews'),

    # Campaign Categories (NEW)
    path('campaign-categories/', views.manage_campaign_categories, name='manage_campaign_categories'),
    path('campaign-categories/create/', views.create_edit_campaign_category, name='create_campaign_category'),
    path('campaign-categories/edit/<int:pk>/', views.create_edit_campaign_category, name='edit_campaign_category'),
    path('campaign-categories/delete/<int:pk>/', views.delete_campaign_category, name='delete_campaign_category'),
    
    # Profile
    path('profile/', views.admin_profile, name='admin_profile'),
    
    # Approval System
    path('approval/ngos/', views.ngo_approval_list, name='ngo_approval_list'),
    path('approval/ngos/<int:user_id>/approve/', views.approve_ngo, name='approve_ngo'),
    path('approval/ngos/<int:user_id>/reject/', views.reject_ngo, name='reject_ngo'),
    
    path('approval/campaigns/', views.campaign_approval_list, name='campaign_approval_list'),
    path('approval/campaigns/<int:campaign_id>/approve/', views.approve_campaign, name='approve_campaign'),
    path('approval/campaigns/<int:campaign_id>/reject/', views.reject_campaign, name='reject_campaign'),
    
    path('approval/donation-requests/', views.donation_request_approval_list, name='donation_request_approval_list'),
    path('approval/donation-requests/<int:request_id>/approve/', views.approve_donation_request, name='approve_donation_request'),
    path('approval/donation-requests/<int:request_id>/reject/', views.reject_donation_request, name='reject_donation_request'),
    
    # Status Updates
    path('claims/<int:claim_id>/update-status/', views.update_claim_status, name='update_claim_status'),
    
    # Delete Actions
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('donations/<int:donation_id>/delete/', views.delete_donation_admin, name='delete_donation_admin'),
    path('campaigns/<int:campaign_id>/delete/', views.delete_campaign, name='delete_campaign'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    
    # Create Operations
    path('admins/create/', views.create_admin, name='create_admin'),
    path('categories/create/', views.create_edit_category, name='create_category'),
    path('categories/<int:category_id>/edit/', views.create_edit_category, name='edit_category'),


    
    # Statistics
    path('stats/', views.system_stats, name='system_stats'),

    # Contact Messages
    path('contact-messages/', views.contact_messages, name='contact_messages'),

    path('rewards/', views.manage_rewards, name='manage_rewards'),
]
