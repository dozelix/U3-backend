from django.urls import path

from .views import api_health, payment_list

urlpatterns = [
    path('health/', api_health, name='api_health'),
    path('payments/', payment_list, name='payment_list'),
]
