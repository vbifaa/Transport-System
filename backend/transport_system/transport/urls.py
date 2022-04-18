from django.urls import include, path
from rest_framework import routers

from .views import BusViewSet, StopViewSet

router = routers.DefaultRouter()
router.register('stops', StopViewSet, basename='stops_api')
router.register('buses', BusViewSet, basename='buses_api')


urlpatterns = [
    path('', include(router.urls))
]
