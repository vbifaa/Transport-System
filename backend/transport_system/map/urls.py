from django.urls import path

from .views import ApiMap

urlpatterns = [
    path('map/', ApiMap.as_view())
]
