from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import Donor, DonationRecord
from .serializers import DonorSerializer, DonorRegisterSerializer, DonorUpdateSerializer, DonationRecordSerializer

class DonorRegisterView(generics.CreateAPIView):
    """Register a new donor"""
    serializer_class = DonorRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Check if user already has a donor profile
        if Donor.objects.filter(user=self.request.user).exists():
            raise PermissionDenied("You already have a donor profile")
        serializer.save(user=self.request.user)

class DonorListView(generics.ListAPIView):
    """List all donors (Admin only)"""
    serializer_class = DonorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_staff:
            return Donor.objects.all()
        # Regular users can only see active donors
        return Donor.objects.filter(is_active=True)

class DonorDetailView(generics.RetrieveAPIView):
    """Get donor details"""
    serializer_class = DonorSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Donor.objects.all()
    lookup_field = 'id'

class DonorUpdateView(generics.UpdateAPIView):
    """Update donor profile"""
    serializer_class = DonorUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only update their own profile
        return Donor.objects.filter(user=self.request.user)
    
    def get_object(self):
        donor = self.get_queryset().first()
        if not donor:
            raise PermissionDenied("You don't have a donor profile")
        return donor

class AdminDonorActionView(generics.UpdateAPIView):
    """Admin actions: approve/deactivate donors"""
    serializer_class = DonorSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Donor.objects.all()
    lookup_field = 'id'
    
    def update(self, request, *args, **kwargs):
        if not request.user.is_admin:
            raise PermissionDenied("Only admin can perform this action")
        
        donor = self.get_object()
        action = request.data.get('action')  # 'approve' or 'deactivate'
        
        if action == 'approve':
            donor.is_active = True
            donor.save()
            return Response({"message": "Donor approved successfully"})
        elif action == 'deactivate':
            donor.is_active = False
            donor.availability_status = 'not_available'
            donor.save()
            return Response({"message": "Donor deactivated successfully"})
        
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class DonationCompleteView(generics.GenericAPIView):
    """Mark donation as completed"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, donor_id):
        try:
            donor = Donor.objects.get(id=donor_id, is_active=True)
        except Donor.DoesNotExist:
            return Response({"error": "Donor not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if donor is eligible
        if not donor.can_donate():
            return Response({
                "error": "Donor is not eligible to donate",
                "days_remaining": donor.days_until_eligible if hasattr(donor, 'days_until_eligible') else 90
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update donor information
        donor.last_donation_date = timezone.now().date()
        donor.availability_status = 'not_available'
        donor.save()
        
        # Create donation record
        donation_record = DonationRecord.objects.create(
            donor=donor,
            recipient_name=request.data.get('recipient_name', ''),
            notes=request.data.get('notes', ''),
            created_by=request.user
        )
        
        serializer = DonationRecordSerializer(donation_record)
        
        return Response({
            "message": "Donation marked as completed successfully",
            "donor_updated": {
                "last_donation_date": donor.last_donation_date,
                "availability_status": donor.availability_status,
                "next_eligible_date": donor.last_donation_date + timedelta(days=settings.DONATION_COOLDOWN_DAYS)
            },
            "donation_record": serializer.data
        }, status=status.HTTP_200_OK)