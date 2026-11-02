from django.urls import path

from .views import cerrar_sesion, iniciar_sesion, inicio

urlpatterns = [
    path('', inicio, name='inicio'),
    path('login/', iniciar_sesion, name='iniciar_sesion'),
    path('logout/', cerrar_sesion, name='cerrar_sesion'),
]
