from django.urls import include, path
from rest_framework import routers

from .views import StopViewSet

router = routers.DefaultRouter()
router.register('stops', StopViewSet, basename='stops_api')


urlpatterns = [
    path('', include(router.urls))
]