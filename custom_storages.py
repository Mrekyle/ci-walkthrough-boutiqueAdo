from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

"""
    Allows us to set the storage location of where we want uploaded images to be saved to. 
    And where all files are to be retrieved from 
"""


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
