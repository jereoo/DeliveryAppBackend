# delivery/serializers.py
from rest_framework import serializers
from .models import Delivery

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ['id', 'customer_name', 'customer_address', 'pickup_location', 'dropoff_location', 'same_pickup_as_customer', 'status', 'created_at']
        # OR: fields = "__all__" to include all model fields