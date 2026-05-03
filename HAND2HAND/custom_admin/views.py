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

