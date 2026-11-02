from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse as api_reverse
from rest_framework_simplejwt.tokens import RefreshToken

SERVICIO_PERMISOS = {
    'dashboard': {'view_dashboard', 'manage_dashboard', 'dashboard', 'ver_panel', 'gestionar_panel'},
    'usuarios': {'view_users', 'manage_users', 'view_usuarios', 'manage_usuarios', 'usuarios', 'ver_usuarios', 'gestionar_usuarios'},
    'pagos': {'view_payments', 'manage_payments', 'view_pagos', 'manage_pagos', 'pagos', 'ver_pagos', 'gestionar_pagos'},
    'reportes': {'view_reports', 'manage_reports', 'view_reportes', 'manage_reportes', 'reportes', 'ver_informes', 'gestionar_informes'},
    'configuracion': {'view_settings', 'manage_settings', 'view_configuracion', 'manage_configuracion', 'configuracion', 'ver_configuracion', 'gestionar_configuracion'},
}


def _normalizar_permiso(nombre):
    if not nombre:
        return ''
    return str(nombre).strip().lower().replace(' ', '_')


def _errores_validacion_password(password, usuario):
    try:
        validate_password(password, user=usuario)
    except ValidationError as error:
        return error.messages
    return []


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'autentificar': api_reverse('autentificar', request=request),
        'agregarusuario': api_reverse('agregarusuario', request=request),
        'actualizar': api_reverse('actualizar', request=request),
        'addpermiso': api_reverse('addpermiso', request=request),
        'asociapermiso': api_reverse('asociapermiso', request=request),
        'token': api_reverse('token_obtain_pair', request=request),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def autentificar(request):
    username = str(request.data.get('username', '')).strip()
    password = str(request.data.get('password', '') or '')

    user = authenticate(username=username, password=password)
    if not user:
        return Response({
            'ok': False,
            'detail': 'Credenciales inválidas.'
        }, status=status.HTTP_401_UNAUTHORIZED)

    permisos = sorted({
        permiso.rsplit('.', 1)[-1]
        for permiso in user.get_all_permissions()
    })

    servicios = {
        servicio: bool(SERVICIO_PERMISOS[servicio].intersection(permisos))
        for servicio in SERVICIO_PERMISOS
    }

    token = RefreshToken.for_user(user)
    return Response({
        'ok': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
        'permisos': permisos,
        'servicios': servicios,
        'token': str(token.access_token),
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def agregarusuario(request):
    username = str(request.data.get('username', '')).strip()
    password = str(request.data.get('password', '') or '')
    email = str(request.data.get('email', '') or '')

    if not username or not password:
        return Response({'ok': False, 'detail': 'Debe ingresar usuario y contraseña.'}, status=status.HTTP_400_BAD_REQUEST)

    errores_password = _errores_validacion_password(
        password,
        User(username=username, email=email),
    )
    if errores_password:
        return Response({
            'ok': False,
            'detail': 'La contraseña no cumple los requisitos.',
            'errors': errores_password,
        }, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'ok': False, 'detail': 'El usuario ya existe.'}, status=status.HTTP_400_BAD_REQUEST)

    usuario = User.objects.create_user(username=username, email=email, password=password)
    return Response({
        'ok': True,
        'user': {
            'id': usuario.id,
            'username': usuario.username,
            'email': usuario.email,
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def actualizar(request):
    username = str(request.data.get('username', '')).strip()
    nueva_password = str(request.data.get('new_password', '') or '')

    if not username or not nueva_password:
        return Response({'ok': False, 'detail': 'Debe indicar usuario y nueva contraseña.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'ok': False, 'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    errores_password = _errores_validacion_password(nueva_password, usuario)
    if errores_password:
        return Response({
            'ok': False,
            'detail': 'La contraseña no cumple los requisitos.',
            'errors': errores_password,
        }, status=status.HTTP_400_BAD_REQUEST)

    usuario.set_password(nueva_password)
    usuario.save()
    return Response({
        'ok': True,
        'detail': 'Contraseña actualizada correctamente.',
        'username': usuario.username,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def addpermiso(request):
    nombre = request.data.get('nombre') or request.data.get('codename')
    if not nombre:
        return Response({'ok': False, 'detail': 'Debe indicar el nombre del permiso.'}, status=status.HTTP_400_BAD_REQUEST)

    codename = _normalizar_permiso(nombre)
    if not codename:
        return Response({'ok': False, 'detail': 'Nombre de permiso inválido.'}, status=status.HTTP_400_BAD_REQUEST)

    content_type = ContentType.objects.get(app_label='auth', model='user')
    permission, created = Permission.objects.get_or_create(
        codename=codename,
        content_type=content_type,
        defaults={'name': str(nombre).strip()}
    )

    return Response({
        'ok': True,
        'creado': created,
        'permiso': {
            'id': permission.id,
            'nombre': permission.name,
            'codename': permission.codename,
        }
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def asociapermiso(request):
    username = str(request.data.get('username', '')).strip()
    permiso = request.data.get('permiso') or request.data.get('nombre') or request.data.get('codename')

    if not username or not permiso:
        return Response({'ok': False, 'detail': 'Debe indicar usuario y permiso.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'ok': False, 'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    permission = Permission.objects.filter(codename=_normalizar_permiso(permiso)).first()
    if permission is None:
        permission = Permission.objects.filter(name__icontains=str(permiso)).first()
    if permission is None:
        return Response({'ok': False, 'detail': 'Permiso no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    usuario.user_permissions.add(permission)
    return Response({
        'ok': True,
        'username': usuario.username,
        'permiso': {
            'id': permission.id,
            'nombre': permission.name,
            'codename': permission.codename,
        },
        'permisos_actuales': sorted(usuario.user_permissions.values_list('codename', flat=True))
    }, status=status.HTTP_200_OK)
