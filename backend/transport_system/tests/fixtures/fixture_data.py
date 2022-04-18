import json
import pytest
import os

from transport_system.actions import get_object_or_404

from transport.models import Bus, Stop, StopDistance


@pytest.fixture
def load_json():
    def run(json_path):
        script_dir = os.path.dirname(__file__)
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
