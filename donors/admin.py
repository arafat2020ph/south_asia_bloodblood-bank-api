from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Donor, DonationRecord

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'blood_group', 'phone_number', 'availability_status', 'is_active', 'last_donation_date')
    list_filter = ('blood_group', 'availability_status', 'is_active', 'whatsapp_available')
    search_fields = ('full_name', 'phone_number', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_donors', 'deactivate_donors']
    
    def approve_donors(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} donor(s) approved.")
    approve_donors.short_description = "Approve selected donors"
    
    def deactivate_donors(self, request, queryset):
        queryset.update(is_active=False, availability_status='not_available')
        self.message_user(request, f"{queryset.count()} donor(s) deactivated.")
    deactivate_donors.short_description = "Deactivate selected donors"

@admin.register(DonationRecord)
class DonationRecordAdmin(admin.ModelAdmin):
    list_display = ('donor', 'donation_date', 'recipient_name', 'created_by')
    list_filter = ('donation_date',)
    search_fields = ('donor__full_name', 'recipient_name')