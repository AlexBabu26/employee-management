from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = (
            UserProfile.Role.ADMIN
            if instance.is_superuser
            else UserProfile.Role.EMPLOYEE
        )
        UserProfile.objects.create(user=instance, role=role)
    else:
        if hasattr(instance, "profile") and instance.is_superuser:
            if instance.profile.role != UserProfile.Role.ADMIN:
                instance.profile.role = UserProfile.Role.ADMIN
                instance.profile.save(update_fields=["role"])
