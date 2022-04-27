from copy import deepcopy
from functools import wraps

from routing.models import Graph
from routing.models import router_wrapper as rw


def mock_router(test):
    @wraps(test)
    def wrapper(*args, **kwargs):
        raw_graph = deepcopy(rw.graph)
        rw.router = None

        if 'router_wrapper' in kwargs:
            new_graph = kwargs['router_wrapper'].graph
        elif 'router_wrapper_with_stops_only' in kwargs:
            new_graph = kwargs['router_wrapper_with_stops_only'].graph
        else:
            new_graph = Graph()
        rw.set_graph(new_graph)

        test(*args, **kwargs)

        rw.set_graph(raw_graph)

    return wrapper
