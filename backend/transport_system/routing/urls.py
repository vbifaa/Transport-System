from django.urls import path

from .views import ApiRoute

urlpatterns = [
    path('route/', ApiRoute.as_view())
]
