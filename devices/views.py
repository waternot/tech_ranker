from rest_framework.viewsets import ModelViewSet
from django.shortcuts import render, get_object_or_404
from .models import Smartphone
from .serializers import SmartphoneSerializer

class SmartphoneViewSet(ModelViewSet):
    queryset = Smartphone.objects.all()
    serializer_class = SmartphoneSerializer

def device_list(request):
    brand_filter = request.GET.get('brand')
    if brand_filter:
        phones = Smartphone.objects.filter(brand__iexact=brand_filter).order_by('-total_score')
    else:
        phones = Smartphone.objects.all().order_by('-total_score')

    brands = Smartphone.objects.values_list('brand', flat=True).distinct()
    return render(request, 'devices/device_list.html', {
        'phones': phones,
        'brands': brands,
        'current_brand': brand_filter
    })

def device_detail(request, pk):
    # Функція для кнопки "Докладніше"
    phone = get_object_or_404(Smartphone, pk=pk)
    return render(request, 'devices/device_detail.html', {'phone': phone})