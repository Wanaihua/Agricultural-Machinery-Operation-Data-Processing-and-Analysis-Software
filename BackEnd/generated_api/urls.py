"""DRF router URLs for the unmanaged database models."""

from rest_framework.routers import DefaultRouter

from .views import (
    DictViewSet,
    FileViewSet,
    ImportLogViewSet,
    MenuViewSet,
    RateViewSet,
    RoleMenuViewSet,
    RoleViewSet,
    TrackViewSet,
    TrackpointsViewSet,
    UserViewSet,
    WorkViewSet,
)

router = DefaultRouter()
router.register(r'dict', DictViewSet, basename='dict')
router.register(r'file', FileViewSet, basename='file')
router.register(r'import_log', ImportLogViewSet, basename='import_log')
router.register(r'menu', MenuViewSet, basename='menu')
router.register(r'rate', RateViewSet, basename='rate')
router.register(r'role', RoleViewSet, basename='role')
router.register(r'role_menu', RoleMenuViewSet, basename='role_menu')
router.register(r'track', TrackViewSet, basename='track')
router.register(r'trackpoints', TrackpointsViewSet, basename='trackpoints')
router.register(r'user', UserViewSet, basename='user')
router.register(r'work', WorkViewSet, basename='work')

urlpatterns = router.urls
