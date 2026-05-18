"""DRF viewsets for the unmanaged database models."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
from .serializers import (
    DictSerializer,
    FileSerializer,
    ImportLogSerializer,
    MenuSerializer,
    RateSerializer,
    RoleMenuSerializer,
    RoleSerializer,
    TrackSerializer,
    TrackpointsSerializer,
    UserSerializer,
    WorkSerializer,
)


class DictViewSet(viewsets.ModelViewSet):
    queryset = Dict.objects.all()
    serializer_class = DictSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('role').all()
    serializer_class = UserSerializer


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer


class ImportLogViewSet(viewsets.ModelViewSet):
    queryset = ImportLog.objects.select_related('admin_id').all()
    serializer_class = ImportLogSerializer


class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.all().prefetch_related('trackpoints')
    serializer_class = TrackSerializer

    @action(detail=True, methods=['get'], url_path='trackpoints')
    def trackpoints(self, request, pk=None):
        track = self.get_object()
        serializer = TrackpointsSerializer(track.trackpoints.all(), many=True)
        return Response(serializer.data)


class TrackpointsViewSet(viewsets.ModelViewSet):
    queryset = Trackpoints.objects.select_related('trackid').all()
    serializer_class = TrackpointsSerializer


class WorkViewSet(viewsets.ModelViewSet):
    queryset = Work.objects.select_related('trackid').all()
    serializer_class = WorkSerializer


class RateViewSet(viewsets.ModelViewSet):
    queryset = Rate.objects.select_related('trackid').all()
    serializer_class = RateSerializer


class RoleMenuViewSet(viewsets.ModelViewSet):
    queryset = RoleMenu.objects.select_related('role_id', 'menu_id').all()
    serializer_class = RoleMenuSerializer
