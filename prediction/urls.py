from django.urls import path
from . import views

urlpatterns = [
    path('', views.predict_crop, name='home'),
    path('predict/', views.predict_crop, name='predict_crop'),
    path('result/<str:predicted_crop>/<str:ai_response>/', views.result_page, name='result_page'),
]
