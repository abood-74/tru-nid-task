from django.urls import path

from .views import EgyptianIDExtractorAPIView

app_name = 'national_ids'

urlpatterns = [
    path('egyptian-id/extract/', EgyptianIDExtractorAPIView.as_view(), name='extract-egyptian-id'),
]