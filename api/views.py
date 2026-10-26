from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentSerializer


@api_view(['GET'])
def api_health(request):
    return Response({
        'status': 'ok',
        'service': 'payment-api',
        'database': 'sqlite',
    })


@api_view(['GET', 'POST'])
def payment_list(request):
    if request.method == 'GET':
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid():
        payment = serializer.save(status='pending')
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
