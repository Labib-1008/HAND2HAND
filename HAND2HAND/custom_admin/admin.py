from django.contrib import admin

# Register your models here.from django.contrib import admin
from donations.models import Reward

# If you want full control
@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_required')
    list_editable = ('points_required',)  # Allow editing directly in list

