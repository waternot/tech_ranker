from rest_framework import serializers
from .models import Smartphone

class SmartphoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Smartphone
        fields = '__all__'