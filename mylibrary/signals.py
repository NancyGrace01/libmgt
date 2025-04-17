from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, AdminProfile

@receiver(post_save, sender=CustomUser)
def create_admin_profile(sender, instance, created, **kwargs):
    if created and instance.role in ['librarian', 'receptionist']:
        AdminProfile.objects.get_or_create(user=instance, role=instance.role)
        
        
        
        
        
        # uxqx cayv gosf cjak
        
        # vajvjnoumirppyhf
