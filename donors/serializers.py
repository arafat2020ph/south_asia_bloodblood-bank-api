from rest_framework import serializers
from .models import Donor, DonationRecord
from accounts.serializers import UserSerializer

class DonorSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    can_donate_now = serializers.SerializerMethodField()
    days_until_eligible = serializers.SerializerMethodField()
    
    class Meta:
        model = Donor
        fields = (
            'id', 'user', 'user_details', 'full_name', 'phone_number',
            'whatsapp_available', 'blood_group', 'latitude', 'longitude',
            'last_donation_date', 'availability_status', 'is_active',
            'can_donate_now', 'days_until_eligible', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_can_donate_now(self, obj):
        return obj.can_donate()
    
    def get_days_until_eligible(self, obj):
        if obj.last_donation_date:
            from django.utils import timezone
            from django.conf import settings
            days_since = (timezone.now().date() - obj.last_donation_date).days
            remaining = settings.DONATION_COOLDOWN_DAYS - days_since
            return max(0, remaining)
        return 0
    
    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits")
        return value
    
    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value
    
    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value

class DonorRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = (
            'full_name', 'phone_number', 'whatsapp_available', 'blood_group',
            'latitude', 'longitude', 'last_donation_date', 'availability_status'
        )
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class DonorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = (
            'full_name', 'phone_number', 'whatsapp_available', 'blood_group',
            'latitude', 'longitude', 'availability_status'
        )

class DonationRecordSerializer(serializers.ModelSerializer):
    donor_details = DonorSerializer(source='donor', read_only=True)
    
    class Meta:
        model = DonationRecord
        fields = ('id', 'donor', 'donor_details', 'donation_date', 
                 'recipient_name', 'notes', 'created_by')
        read_only_fields = ('id', 'donation_date')