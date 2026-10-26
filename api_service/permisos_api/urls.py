from django.urls import path

from .views import addpermiso, agregausuario, asociapermiso, autentificar, actualizar

urlpatterns = [
    path('autentificar/', autentificar, name='autentificar'),
    path('agregarusuario/', agregausuario, name='agregarusuario'),
    path('actualizar/', actualizar, name='actualizar'),
    path('addpermiso/', addpermiso, name='addpermiso'),
    path('asociapermiso/', asociapermiso, name='asociapermiso'),
]
