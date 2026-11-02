from rest_framework import serializers


class AutentificarSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )


class AgregarUsuarioSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )
    email = serializers.CharField(required=False, allow_blank=True, max_length=254)


class ActualizarSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )


class AddPermisoSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=False, allow_blank=True, max_length=255)
    codename = serializers.CharField(required=False, allow_blank=True, max_length=100)


class AsociaPermisoSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    permiso = serializers.CharField(required=False, allow_blank=True, max_length=255)
    nombre = serializers.CharField(required=False, allow_blank=True, max_length=255)
    codename = serializers.CharField(required=False, allow_blank=True, max_length=100)
