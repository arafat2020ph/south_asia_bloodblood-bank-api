from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom User model for the blood bank system"""
    phone_number = models.CharField(max_length=15, unique=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} - {self.phone_number}"
