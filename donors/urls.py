from django.urls import path
from .views import (
    DonorRegisterView, DonorListView, DonorDetailView,
    DonorUpdateView, AdminDonorActionView, DonationCompleteView
)

urlpatterns = [
    path('register/', DonorRegisterView.as_view(), name='donor-register'),
    path('', DonorListView.as_view(), name='donor-list'),
    path('<int:id>/', DonorDetailView.as_view(), name='donor-detail'),
    path('update/', DonorUpdateView.as_view(), name='donor-update'),
    path('admin/<int:id>/action/', AdminDonorActionView.as_view(), name='admin-action'),
    path('donate/<int:donor_id>/', DonationCompleteView.as_view(), name='donation-complete'),
]