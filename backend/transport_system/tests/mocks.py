from copy import deepcopy
from functools import wraps

from map.views import settings as draw_settings
from routing.models import Router
from routing.models import router_wrapper as rw


def mock_router(test):
    @wraps(test)
    def wrapper(*args, **kwargs):
        raw_router = deepcopy(rw.router)
        rw.router = None

        if 'router_wrapper' in kwargs:
            new_router = kwargs['router_wrapper'].router
        elif 'router_wrapper_with_stops_only' in kwargs:
            new_router = kwargs['router_wrapper_with_stops_only'].router
        else:
            new_router = Router(empty=True)
        rw.router = new_router

        test(*args, **kwargs)

        rw.router = raw_router

    return wrapper


def mock_dwg(test):
    @wraps(test)
    def wrapper(*args, **kwargs):
        tmp_dwg = deepcopy(draw_settings.dwg)

        draw_settings.dwg = None

        test(*args, **kwargs)

        draw_settings.dwg = tmp_dwg

    return wrapper
