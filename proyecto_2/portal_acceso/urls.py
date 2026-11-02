from django.urls import path

from .views import cerrar_sesion, iniciar_sesion, inicio, seccion

urlpatterns = [
    path('', inicio, name='inicio'),
    path('login/', iniciar_sesion, name='iniciar_sesion'),
    path('logout/', cerrar_sesion, name='cerrar_sesion'),
    path('usuarios/', seccion, {'seccion': 'usuarios'}, name='usuarios'),
    path('pagos/', seccion, {'seccion': 'pagos'}, name='pagos'),
    path('reportes/', seccion, {'seccion': 'reportes'}, name='reportes'),
    path('configuracion/', seccion, {'seccion': 'configuracion'}, name='configuracion'),
]
