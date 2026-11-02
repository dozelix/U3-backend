from django.urls import path

from .views import (
    ActualizarView,
    AddPermisoView,
    AgregarUsuarioView,
    AsociaPermisoView,
    AutentificarView,
)

urlpatterns = [
    path('autentificar/', AutentificarView.as_view(), name='autentificar'),
    path('agregarusuario/', AgregarUsuarioView.as_view(), name='agregarusuario'),
    path('actualizar/', ActualizarView.as_view(), name='actualizar'),
    path('addpermiso/', AddPermisoView.as_view(), name='addpermiso'),
    path('asociapermiso/', AsociaPermisoView.as_view(), name='asociapermiso'),
]
