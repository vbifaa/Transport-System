from django.urls import path

from .views import map, map_route

urlpatterns = [
    path('map/', map, name='map'),
    path('map/route/', map_route, name='map_route')
]
