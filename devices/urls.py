from django.urls import path
from . import views

urlpatterns = [
    path('', views.device_list,name='device_list'),
    path('device/<int:pk>/', views.device_detail, name='device_detail'),
    ]