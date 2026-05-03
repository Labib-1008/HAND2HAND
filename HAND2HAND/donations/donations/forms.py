# donations/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    User, DonorRecipientProfile, Category, DonationItem, 
    DonationImage, DonationClaim, DonationReview, RequestItem,DonationToRequest
)

from django.core.exceptions import ValidationError
from django.utils import timezone




# ===== USER FORMS =====
class CustomUserCreationForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('donor/recipient', 'Donor/Recipient'),
        ('ngo', 'NGO'),
    )
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'user_type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'user_type', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


# ===== PROFILE FORM =====
class DonorRecipientProfileForm(forms.ModelForm):
    class Meta:
        model = DonorRecipientProfile
        fields = [
            'full_name', 'email', 'nid_birth_certificate', 
            'city_postal', 'address', 'mobile_number'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})




# ===== DONATION ITEM FORM =====

class DonationItemForm(forms.ModelForm):
    # Single image upload field
    image = forms.ImageField(
        required=False,  # make optional for editing
        label="Upload Image",
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control',
            'id': 'id_image',  # single image id
        })
    )

    class Meta:
        model = DonationItem
        fields = [
            'title', 'category', 'quantity', 'description',
            'location', 'urgency', 'notify_immediately'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the item condition, specifications, and other details...',
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Enter city or area',
                'class': 'form-control'
            }),
            'urgency': forms.Select(attrs={'class': 'form-control'}),
            'notify_immediately': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = True
        self.fields['location'].required = True


# ===== DONATION CLAIM FORM =====
class DonationClaimForm(forms.ModelForm):
    class Meta:
        model = DonationClaim
        fields = ['message', 'preferred_date', 'contact_number']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Explain why you need this donation and how you plan to use it...'
            }),
            'preferred_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'contact_number': forms.TextInput(attrs={
                'placeholder': 'Your phone number for coordination'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Bootstrap class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        # Required fields
        self.fields['message'].required = True
        self.fields['contact_number'].required = True

    def clean_contact_number(self):
        """ ফোন নাম্বার validation """
        contact = self.cleaned_data.get('contact_number')
        if contact and not contact.isdigit():
            raise forms.ValidationError("Contact number should only contain digits.")
        if contact and len(contact) < 10:
            raise forms.ValidationError("Enter a valid phone number.")
        return contact

    def clean_preferred_date(self):
        """ Date validation (past তারিখ allow করা যাবে না) """
        date = self.cleaned_data.get('preferred_date')
        if date:
            from django.utils import timezone
            if date < timezone.now():
                raise forms.ValidationError("Preferred date cannot be in the past.")
        return date


# ===== DONATION REVIEW FORM =====

class DonationReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    ]

    rating = forms.IntegerField(
    widget=forms.HiddenInput()
    )

    class Meta:
        model = DonationReview
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your experience with this donation. Was the item as described? How was the pickup process?'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap or custom form-control class
        self.fields['comment'].widget.attrs.update({'class': 'form-control'})
        # Hide default radio buttons (we’ll show stars via CSS/JS)
        self.fields['rating'].widget.attrs.update({'style': 'display:none;'})




# ===== Request Item FORM =====

class RequestItemForm(forms.ModelForm):
    class Meta:
        model = RequestItem
        fields = [
            'image',
            'title',
            'category',
            'quantity',
            'description',
            'needed_before',
            'delivery_location',
            'contact_number',
            'notify_immediately',
            'urgency',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g., Need school supplies for underprivileged children'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Please describe what you need, why you need it, and how it will be used...'
            }),
            'needed_before': forms.DateInput(attrs={
                'type': 'date'
            }),
            'delivery_location': forms.TextInput(attrs={
                'placeholder': 'Enter delivery / pickup location'
            }),
            'contact_number': forms.TextInput(attrs={
                'placeholder': 'Enter phone or WhatsApp number'
            }),
            'urgency': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()
        # Optional: Set category empty label
        if 'category' in self.fields:
            self.fields['category'].empty_label = "Select a category"
        # Optional: Add help text for notify_immediately
        if 'notify_immediately' in self.fields:
            self.fields['notify_immediately'].help_text = "Check to notify admins immediately for urgent requests."

    # Validation for needed_before
    def clean_needed_before(self):
        needed_before = self.cleaned_data.get('needed_before')
        if needed_before and needed_before < timezone.now().date():
            raise ValidationError("The needed date cannot be in the past.")
        return needed_before

    # Validation for quantity
    def clean_quantity(self):
     quantity = self.cleaned_data.get('quantity')
     if quantity is not None and quantity < 1:
        raise ValidationError("Quantity must be at least 1.")
     return quantity





# ===== SEARCH AND FILTER FORM =====
class DonationSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search donations...',
            'class': 'form-control'
        })
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Location...',
            'class': 'form-control'
        })
    )

    urgency = forms.ChoiceField(
        choices=[('', 'Any Urgency')] + list(DonationItem.URGENCY_LEVELS),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )



# ===== PASSWORD CHANGE FORM =====
class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )


# ===== DONATION TO REQUEST FORM =====

class DonationToRequestForm(forms.ModelForm):
    class Meta:
        model = DonationToRequest
        fields = ['title', 'description', 'quantity', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Donation Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description (optional)'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }



class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Your Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input', 'placeholder': 'Your Email'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-textarea', 'placeholder': 'Your Message'
    }))