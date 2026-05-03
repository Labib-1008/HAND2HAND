from django import forms
from .models import Campaign, CampaignCategory, NGODonation, NGOProfile


# ===== NGO PROFILE FORM =====
class NGOProfileForm(forms.ModelForm):
    class Meta:
        model = NGOProfile
        fields = [
            'ngo_name', 
            'reg_certificate',
            'email',
            'contact_person',
            'nid_birth_certificate',
            'city_postal',
            'address',
            'ngo_type',
            'social_link',
            'mobile_number',  # add mobile here
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'description', 'image', 'goal_amount', 'end_date', 'category']  # category added
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter campaign title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Write details...'
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'goal_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),  # dropdown for categories
        }




        

class NGODonationForm(forms.ModelForm):
    payer_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name (optional)'
        })
    )
    payment_method = forms.ChoiceField(
        required=True,
        choices=[
            ('bkash', 'Bkash'),
            ('nagad', 'Nagad'),
            ('card', 'Card')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    account_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Account / Mobile (optional)'
        })
    )
    is_anonymous = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )

    class Meta:
        model = NGODonation
        fields = [
            'amount', 'message', 'payer_name',
            'payment_method', 'account_input', 'is_anonymous'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter donation amount',
                'min': 1
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional message'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError("Donation amount must be greater than 0.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('is_anonymous'):
            cleaned_data['payer_name'] = ''
            cleaned_data['account_input'] = ''
        return cleaned_data
