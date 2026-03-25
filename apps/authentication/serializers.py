from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "nombre", "email", "password", "rol"]
        extra_kwargs = {"rol": {"required": False}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Credenciales incorrectas")
        if not user.activo:
            raise serializers.ValidationError("Cuenta desactivada")
        data["user"] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nombre", "email", "rol", "activo", "fecha_creacion"]
        read_only_fields = ["id", "fecha_creacion"]
