from django.urls import path, include
from . import views

from rest_framework.routers import DefaultRouter

from .views import SmartphoneViewSet

router = DefaultRouter()
router.register('smartphones', SmartphoneViewSet)

urlpatterns = [
    path('', views.device_list,name='device_list'),
    path('device/<int:pk>/', views.device_detail, name='device_detail'),
    path('api/', include(router.urls)),
    ]