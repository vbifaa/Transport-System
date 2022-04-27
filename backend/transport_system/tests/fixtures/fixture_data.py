import json
import os

import pytest

from routing.models import Edge, Graph, RouterWrapper
from transport.models import Bus, Stop, StopDistance
from transport_system.actions import get_object_or_404


@pytest.fixture
def load_json():
    def run(json_path):
        script_dir = os.path.dirname(__file__)
        if json_path == '1':
            print(script_dir)
            assert False
        file_path = os.path.join(script_dir, json_path)
        with open(file_path) as f:
            return json.load(f)
    return run


@pytest.fixture
def stops(load_json):
    json_stops = load_json('stops.json')

    for stop in json_stops:
        Stop.objects.create(**stop)

    json_stops_dist = load_json('stop_distances.json')
    for stop_dist in json_stops_dist:
        from_stop = get_object_or_404(
            Stop, name=stop_dist['from'], msg='Cant find from_stop',
        )
        to_stop = get_object_or_404(
            Stop, name=stop_dist['to'], msg='Cant find to_stop',
        )

        StopDistance.objects.create(
            from_stop=from_stop,
            to_stop=to_stop,
            distance=stop_dist['distance'],
        )

    return Stop.objects.all()


@pytest.fixture
def response_buses(load_json, stops):
    json_buses = load_json('buses.json')

    for bus in json_buses:
        Bus.objects.create(**bus)

    return Bus.objects.all()


@pytest.fixture
def graph_1():
    res = Graph()
    for _ in range(2):
        res.add_vertex()
    res.add_edge(Edge(from_v=0, to_v=1, weight=5))
    res.add_edge(Edge(from_v=1, to_v=0, weight=10))
    return res


@pytest.fixture
def graph_2():
    res = Graph()
    for _ in range(5):
        res.add_vertex()
    res.add_edge(Edge(from_v=1, to_v=1, weight=5))
    res.add_edge(Edge(from_v=1, to_v=2, weight=10))
    res.add_edge(Edge(from_v=2, to_v=3, weight=15))
    res.add_edge(Edge(from_v=3, to_v=1, weight=20))
    res.add_edge(Edge(from_v=3, to_v=4, weight=17))
    res.add_edge(Edge(from_v=4, to_v=2, weight=23))
    res.add_edge(Edge(from_v=4, to_v=1, weight=40))
    return res


@pytest.fixture
def router_wrapper_with_stops_only(load_json, stops):
    router_wrapper = RouterWrapper(Graph())

    json_stops = load_json('stops.json')
    for stop in json_stops:
        router_wrapper.add_stop(stop['name'])
    return router_wrapper


@pytest.fixture
def router_wrapper(response_buses, router_wrapper_with_stops_only):
    router_wrapper_with_stops_only.add_bus(
        bus_name='297',
        stops=[
            'Biryulyovo Zapadnoye',
            'Biryulyovo Tovarnaya',
            'Universam',
            'Biryusinka',
            'Apteka',
            'Biryulyovo Zapadnoye'
        ],
        one_direction=True,
    )
    router_wrapper_with_stops_only.add_bus(
        bus_name='750',
        stops=[
            'Tolstopaltsevo',
            'Rasskazovka'
        ],
        one_direction=False,
    )
    router_wrapper_with_stops_only.add_bus(
        bus_name='635',
        stops=[
            'Biryulyovo Tovarnaya',
            'Universam',
            'Biryusinka',
            'TETs 26',
            'Pokrovskaya',
            'Prazhskaya'
        ],
        one_direction=False,
    )
    router_wrapper_with_stops_only.add_bus(
        bus_name='828',
        stops=[
            'Biryulyovo Zapadnoye',
            'TETs 26',
            'Biryusinka',
            'Universam',
            'Pokrovskaya',
            'Rossoshanskaya ulitsa'
        ],
        one_direction=False,
    )
    return router_wrapper_with_stops_only
