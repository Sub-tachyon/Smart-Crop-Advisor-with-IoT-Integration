from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('predict/', views.predict_crop, name='predict_crop'),
    path('result/', views.result_page, name='result_page'),
    path('fetch-iot-data/', views.fetch_iot_data, name='fetch_iot_data'),
]