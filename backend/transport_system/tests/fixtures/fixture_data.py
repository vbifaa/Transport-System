import json
import os

import pytest

from map.models import MapBus
from routing.models import Edge, Graph, RouterWrapper
from transport.models import Bus, BusStop, Stop, StopDistance
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


@pytest.fixture
def backward_bus():
    create_bus(
        name='236',
        type='BACKWARD',
        stops=['Astankino', 'Vazhino', 'Kalugino'],
    )


@pytest.fixture
def round_bus():
    create_bus(
        name='849',
        type='ROUND',
        stops=['AstankinoR', 'VazhinoR', 'KaluginoR', 'AstankinoR'],
    )


@pytest.fixture
def round_bus_two_support():
    create_bus(
        name='849',
        type='ROUND',
        stops=['Astankino', 'Vazhino', 'Kalugino', 'Astankino'],
    )
    create_bus(
        name='345',
        type='BACKWARD',
        stops=['Vazhino', 'Gamino', 'Lazino'],
    )


@pytest.fixture
def round_bus_three_support():
    create_bus(
        name='849',
        type='ROUND',
        stops=['Astankino', 'Vazhino', 'Vaznaya', 'Kalugino', 'Astankino'],
    )
    create_bus(
        name='345',
        type='BACKWARD',
        stops=['Vazhino', 'Gamino', 'Lazino'],
    )
    create_bus(
        name='462',
        type='BACKWARD',
        stops=['Vaznaya', 'Gamino2', 'Lazino2'],
    )


def create_bus(stops, name, type):
    b = Bus.objects.create(
        name=name,
        velocity=40,
        stop_count=4,
        route_length=27600,
        unique_stop_count=3,
    )
    for stop in stops:
        o, _ = Stop.objects.get_or_create(name=stop, latitude=0, longitude=0)
        BusStop.objects.get_or_create(stop=o, bus=b)

    MapBus.objects.create(
        name=name,
        type=type,
        stops=stops,
    )


@pytest.fixture
def map_buses(load_json, response_buses):
    buses = load_json('map_buses.json')

    for bus in buses:
        b = Bus.objects.get(name=bus['name'])
        for stop in bus['stops']:
            s = Stop.objects.get(name=stop)
            BusStop.objects.get_or_create(stop=s, bus=b)

        MapBus.objects.create(
            name=bus['name'],
            type='ROUND' if bus['is_roundtrip'] else 'BACKWARD',
            stops=bus['stops'],
        )


@pytest.fixture
def map_stops_with_coordeinates():
    Stop.objects.create(name='start', longitude=0.0, latitude=0.0)
    Stop.objects.create(name='inter1', longitude=53.34517, latitude=37.12098)
    Stop.objects.create(name='inter2', longitude=4.6, latitude=4.2)
    Stop.objects.create(name='inter3', longitude=29.38944, latitude=86.28910)
    Stop.objects.create(name='finish', longitude=3.2, latitude=5.0)

    MapBus.objects.create(
        name='345',
        type='BACKWARD',
        stops=['start', 'inter1', 'inter2', 'inter3', 'finish'],
    )
