"""Auto-generated DRF router URLs."""

from rest_framework.routers import DefaultRouter
from .views import (
    DictViewSet,
    FileViewSet,
    ImportLogViewSet,
    MachineryTrackViewSet,
    MenuViewSet,
    RoleViewSet,
    RoleMenuViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'dict', DictViewSet, basename='dict')
router.register(r'file', FileViewSet, basename='file')
router.register(r'import_log', ImportLogViewSet, basename='import_log')
router.register(r'machinery_track', MachineryTrackViewSet, basename='machinery_track')
router.register(r'menu', MenuViewSet, basename='menu')
router.register(r'role', RoleViewSet, basename='role')
router.register(r'role_menu', RoleMenuViewSet, basename='role_menu')
router.register(r'user', UserViewSet, basename='user')

urlpatterns = router.urls
