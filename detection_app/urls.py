# detection_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
    #path('loading/<int:image_id>/', views.loading, name='loading'),
    path('results/<int:image_id>/', views.detection_results, name='detection_results'),
    path('check_detection_status/<int:image_id>/', views.check_detection_status, name='check_detection_status'),
    path('gallery/', views.gallery_detected, name='gallery_detected')
]
