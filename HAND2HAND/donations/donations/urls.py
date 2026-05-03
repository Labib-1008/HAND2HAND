from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup, name="signup"),

    # Explore pages
    path("explore/", views.explore_donations, name="explore_donations"),

    # Donation actions
    path("donate/", views.donate_item, name="donate_item"),
    path('request-item/', views.request_item, name='request_item'),
    path("request/<int:pk>/", views.request_detail, name="request_detail"),
    path("donate-to-requests/", views.donate_to_requests, name="donate_to_requests"),

    # My Requests (user’s own requests)
    path('my-requests/', views.my_requests, name='my_requests'),
    path("request/<int:pk>/edit/", views.edit_request, name="edit_request"),
    path("request/<int:pk>/delete/", views.delete_request, name="delete_request"),

    # donate to a specific request (Donate button link)
    path('donate-request/<int:request_id>/', views.donate_item_to_request, name='donate_item_to_request'),
    path('mark-received/<int:donation_id>/', views.mark_received, name='mark_received'),

    # Donation detail, claim, review
    path("donation/<int:item_id>/", views.donation_detail, name="donation_detail"),
    path("donation/<int:item_id>/claim/", views.claim_donation, name="claim_donation"),
    path('claim/<int:claim_id>/complete/', views.complete_claim, name='complete_claim'),
    path("claim/<int:claim_id>/review/", views.submit_review, name="submit_review"),
    path('claim/<int:claim_id>/<str:action>/', views.handle_claim, name='handle_claim'),
    

    
    

    # User donations & profile
    path("my-donations/", views.my_donations, name="my_donations"),
    path('my-claims/', views.my_claims, name='my_claims'),
    path('donation/<int:item_id>/edit/', views.edit_donation, name='edit_donation'),
    path('donation/<int:item_id>/delete/', views.delete_donation, name='delete_donation'),
    
    path("profile/", views.profile, name="profile"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path("profile/change-password/", views.change_password, name="change_password"),
    path("profile/upload-photo/", views.upload_photo, name="upload_photo"),
    path("my-rewards/", views.my_rewards, name="my_rewards"),



    # Notifications
    path('notifications/', views.notifications_page, name='notifications_page'),
]
