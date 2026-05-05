from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q, F, FloatField, Value
from django.db.models.functions import Cast
from donors.models import Donor
from donors.serializers import DonorSerializer
from .distance import haversine_distance, calculate_bounding_box

class DonorSearchView(generics.ListAPIView):
    """Search for nearby donors based on blood group and location"""
    serializer_class = DonorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Get search parameters
        blood_group = self.request.query_params.get('blood_group')
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius', 10)
        
        # Validate required parameters
        if not blood_group:
            raise ValidationError({"blood_group": "Blood group is required"})
        if not lat or not lng:
            raise ValidationError({"location": "Latitude and longitude are required"})
        
        try:
            lat = float(lat)
            lng = float(lng)
            radius = float(radius)
        except ValueError:
            raise ValidationError({"coordinates": "Invalid latitude or longitude values"})
        
        if radius > 100:
            raise ValidationError({"radius": "Radius cannot exceed 100 km"})
        
        # First, get all available and active donors with matching blood group
        donors = Donor.objects.filter(
            blood_group=blood_group,
            availability_status='available',
            is_active=True
        )
        
        # Update availability for all donors (auto-update based on 90 days rule)
        for donor in donors:
            donor.update_availability()
        
        # Refresh queryset after updates
        donors = Donor.objects.filter(
            blood_group=blood_group,
            availability_status='available',
            is_active=True
        )
        
        # Calculate bounding box for initial filter
        min_lat, max_lat, min_lon, max_lon = calculate_bounding_box(lat, lng, radius)
        
        # Filter donors within bounding box
        donors = donors.filter(
            latitude__gte=min_lat,
            latitude__lte=max_lat,
            longitude__gte=min_lon,
            longitude__lte=max_lon
        )
        
        # Calculate exact distances and filter by radius
        donor_list_with_distance = []
        for donor in donors:
            distance = haversine_distance(lat, lng, donor.latitude, donor.longitude)
            if distance <= radius:
                donor_list_with_distance.append((donor, distance))
        
        # Sort by distance
        donor_list_with_distance.sort(key=lambda x: x[1])
        
        # Store distances for serialization
        self.distances = {donor.id: distance for donor, distance in donor_list_with_distance}
        
        # Return sorted donors
        return [donor for donor, _ in donor_list_with_distance]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Add distance to each donor in response
        response_data = []
        for donor_data in serializer.data:
            donor_id = donor_data['id']
            donor_data['distance_km'] = round(self.distances.get(donor_id, 0), 2)
            response_data.append(donor_data)
        
        return Response({
            "count": len(response_data),
            "search_params": {
                "blood_group": request.query_params.get('blood_group'),
                "radius_km": float(request.query_params.get('radius', 10)),
                "center_latitude": float(request.query_params.get('lat')),
                "center_longitude": float(request.query_params.get('lng'))
            },
            "results": response_data
        })