# import os

from copy import deepcopy
from functools import wraps

# from map.views import FILE_PATH, MAP_BUILD
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


# def mock_file_path(test):
#     @wraps(test)
#     def wrapper(*args, **kwargs):
#         global FILE_PATH
#         global MAP_BUILD

#         tmp_file_path_value = copy(FILE_PATH)
#         tmp_map_build_value = copy(MAP_BUILD)

#         FILE_PATH = 'tests/fixtures/tmp.svg'
#         MAP_BUILD = False

#         test(*args, **kwargs)

#         FILE_PATH = tmp_file_path_value
#         MAP_BUILD = tmp_map_build_value

#         script_dir = os.path.dirname(__file__)
#         os.remove(os.path.join(script_dir, 'tmp.svg'))

#     return wrapper
