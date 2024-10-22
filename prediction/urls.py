from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # This defines the home URL pattern
    path('predict/', views.predict_crop, name='predict_crop'),
    path('result/', views.result_page, name='result_page'),
]