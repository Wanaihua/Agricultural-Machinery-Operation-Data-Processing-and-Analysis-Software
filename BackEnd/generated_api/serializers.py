"""DRF serializers for the unmanaged database models."""

from rest_framework import serializers

from .models import (
    Dict,
    File,
    ImportLog,
    Menu,
    Rate,
    Role,
    RoleMenu,
    Track,
    Trackpoints,
    User,
    Work,
)


class DictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dict
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class ImportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportLog
        fields = '__all__'


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = '__all__'


class TrackpointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trackpoints
        fields = '__all__'


class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = '__all__'


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = '__all__'


class RoleMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleMenu
        fields = '__all__'
