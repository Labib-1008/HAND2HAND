# ngos/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import NGODonation, Campaign

@receiver(post_save, sender=NGODonation)
def update_campaign_collected_on_save(sender, instance, created, **kwargs):
    """Update campaign collected_amount after new donation"""
    if created:
        campaign = instance.campaign
        campaign.collected_amount += instance.amount
        campaign.save(update_fields=["collected_amount"])

@receiver(post_delete, sender=NGODonation)
def update_campaign_collected_on_delete(sender, instance, **kwargs):
    """Adjust campaign collected_amount if a donation is deleted"""
    campaign = instance.campaign
    campaign.collected_amount -= instance.amount
    if campaign.collected_amount < 0:
        campaign.collected_amount = 0
    campaign.save(update_fields=["collected_amount"])
