from django.db import models
from django_countries.fields import CountryField
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Importing the user model from django auth
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    """
        A user profile model being imported from the django user model.
        Allowing a user to see there past order history, Payment information
        Delivery information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_email = models.EmailField(max_length=254, null=True, blank=True)
    default_phone_number = models.CharField(
        max_length=20, null=True, blank=True)
    # Requires the blank label as drop down selectors dont have a placeholder option
    default_country = CountryField(
        blank_label='Country *', null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_town_or_city = models.CharField(
        max_length=40, null=True, blank=True)
    default_street_address1 = models.CharField(
        max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(
        max_length=80, null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
        Updates or saves the user profile
    """

    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()
