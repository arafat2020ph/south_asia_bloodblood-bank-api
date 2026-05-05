from django.urls import path
from .views import DonorSearchView

urlpatterns = [
    path('', DonorSearchView.as_view(), name='donor-search'),
]