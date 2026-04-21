"""Auto-generated DRF viewsets."""

from rest_framework import viewsets
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
from .serializers import (
    DictSerializer,
    FileSerializer,
    ImportLogSerializer,
    MachineryTrackSerializer,
    MenuSerializer,
    RoleSerializer,
    RoleMenuSerializer,
    UserSerializer,
)

class DictViewSet(viewsets.ModelViewSet):
    queryset = Dict.objects.all()
    serializer_class = DictSerializer

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

class ImportLogViewSet(viewsets.ModelViewSet):
    queryset = ImportLog.objects.all()
    serializer_class = ImportLogSerializer

class MachineryTrackViewSet(viewsets.ModelViewSet):
    queryset = MachineryTrack.objects.all()
    serializer_class = MachineryTrackSerializer

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class RoleMenuViewSet(viewsets.ModelViewSet):
    queryset = RoleMenu.objects.all()
    serializer_class = RoleMenuSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
