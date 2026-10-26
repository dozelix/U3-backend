from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'reference',
            'amount',
            'currency',
            'method',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'status', 'created_at']
