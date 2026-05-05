from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
from accounts.models import User

class Donor(models.Model):
    """Donor model for blood donation management"""
    
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    AVAILABILITY_STATUS = [
        ('available', 'Available'),
        ('not_available', 'Not Available'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, unique=True)
    whatsapp_available = models.BooleanField(default=False)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    last_donation_date = models.DateField(null=True, blank=True)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_STATUS, default='available')
    is_active = models.BooleanField(default=True)  # Admin approved
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'donors'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['blood_group', 'availability_status', 'is_active']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.blood_group}"
    
    def can_donate(self):
        """Check if donor is eligible to donate"""
        if not self.is_active or self.availability_status == 'not_available':
            return False
        
        if self.last_donation_date:
            days_since_last_donation = (timezone.now().date() - self.last_donation_date).days
            if days_since_last_donation < 90:
                return False
        
        return True
    
    def update_availability(self):
        """Auto-update availability based on last donation date"""
        from django.conf import settings
        
        if self.last_donation_date:
            days_since_last_donation = (timezone.now().date() - self.last_donation_date).days
            if days_since_last_donation >= settings.DONATION_COOLDOWN_DAYS:
                if self.availability_status == 'not_available':
                    self.availability_status = 'available'
                    self.save(update_fields=['availability_status'])
    
    def save(self, *args, **kwargs):
        # Auto-update availability before saving
        if self.last_donation_date:
            from django.conf import settings
            days_since_last_donation = (timezone.now().date() - self.last_donation_date).days
            if days_since_last_donation >= settings.DONATION_COOLDOWN_DAYS:
                self.availability_status = 'available'
        super().save(*args, **kwargs)

class DonationRecord(models.Model):
    """Track donation history"""
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    donation_date = models.DateField(auto_now_add=True)
    recipient_name = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='donations_created')
    
    class Meta:
        db_table = 'donation_records'
        ordering = ['-donation_date']
    
    def __str__(self):
        return f"{self.donor.full_name} - {self.donation_date}"