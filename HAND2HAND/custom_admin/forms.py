# custom_admin/forms.py

from django import forms
from donations.models import Category, Notification, User, DonationItem, AskForDonation, DonationClaim, Reward


# ===== CATEGORY FORM =====
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter category description...',
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category name'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'FontAwesome icon class (e.g., fas fa-book)'
            }),
        }

# ===== NOTIFICATION FORM =====
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['user', 'message', 'link', 'is_read']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Notification message...'
            }),
            'link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional URL link'
            }),
            'is_read': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ===== USER ADMIN FORM =====
class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'user_type', 
                 'is_approved', 'is_active', 'is_staff', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# ===== DONATION ITEM ADMIN FORM =====
class DonationItemAdminForm(forms.ModelForm):
    class Meta:
        model = DonationItem
        fields = ['title', 'donor', 'category', 'quantity', 'description', 
                 'location', 'status', 'urgency', 'is_verified', 'expiry_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'donor': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'urgency': forms.Select(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }

# ===== BULK ACTION FORM =====
class BulkActionForm(forms.Form):
    ACTION_CHOICES = [
        ('approve', 'Approve Selected'),
        ('reject', 'Reject Selected'),
        ('delete', 'Delete Selected'),
    ]
    
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control',
        'onchange': 'this.form.submit()'
    }))
    items = forms.ModelMultipleChoiceField(
        queryset=AskForDonation.objects.all(),
        widget=forms.MultipleHiddenInput
    )

# ===== SYSTEM SETTINGS FORM =====
class SystemSettingsForm(forms.Form):
    site_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    site_description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    items_per_page = forms.IntegerField(
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    auto_approve_donations = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )





class RewardThresholdForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = ['points_required']
        widgets = {
            'points_required': forms.NumberInput(attrs={
                'class': 'form-control reward-input',
                'min': 0,
                'style': 'max-width:150px;',
            })
        }
