"""Auto-generated DRF serializers."""

from rest_framework import serializers
from .models import (
    Dict,
    File,
    ImportLog,
    MachineryTrack,
    Menu,
    Role,
    RoleMenu,
    User,
)

class DictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dict
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

class ImportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportLog
        fields = '__all__'

class MachineryTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineryTrack
        fields = '__all__'

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class RoleMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleMenu
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
