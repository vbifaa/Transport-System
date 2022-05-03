from collections import defaultdict, OrderedDict
from pickle import STOP
from re import X
import typing

from transport.models import Stop

from .models import MapBus, MapStop


def gluing():
    support_stops = set_support_stops()
    x_coord, y_coord = interpolation(support_stops)
    neighboors = set_neighboors()

    x_indx: typing.Dict[str, int] = {}
    for _, stop in x_coord.items():
        max_neighb = -1
        for neighb in neighboors[stop]:
            neighb_indx = x_indx.get(neighb, -1)
            max_neighb = max(max_neighb, neighb_indx)
        x_indx[stop] = max_neighb + 1

    y_indx: typing.Dict[str, int] = {}
    xy_indx: typing.Dict[int, int] = {}
    for _, stop in y_coord.items():
        x_id = x_indx[stop]
        max_neighb = xy_indx.get(x_id, -1)
        for neighb in neighboors[stop]:
            neighb_indx = y_indx.get(neighb, -1)
            max_neighb = max(max_neighb, neighb_indx)
        y_indx[stop] = max_neighb + 1
        xy_indx[x_id] = max_neighb + 1

    print(x_indx)
    print(y_indx)
    for stop in Stop.objects.all():
        name = stop.name
        MapStop.objects.create(
            name=name, x_map_id=x_indx[name], y_map_id=y_indx[name],
        )



def set_support_stops() -> typing.Set[str]:
    stops = Stop.objects.prefetch_related('buses').all()

    support_stops = set()
    bus_support_stops_count = defaultdict(int)

    for stop in stops:
        if stop.buses.count() > 1:
            support_stops.add(stop.name)
            for bus in stop.buses.all():
                bus_support_stops_count[bus.name] += 1
        if stop.buses.count() == 0:
            support_stops.add(stop.name)

    buses = MapBus.objects.all()
    for bus in buses:
        bus_stops = bus.stops

        if bus.type == 'ROUND':
            main_stop = bus_stops[0]
            if main_stop not in support_stops:
                bus_support_stops_count[bus.name] += 1
            support_stops.add(main_stop)
            if bus_support_stops_count[bus.name] == 1:
                n = len(bus_stops) - 1
                id_1 = n // 3
                id_2 = (n // 3) * 2
                support_stops.add(bus_stops[id_1])
                support_stops.add(bus_stops[id_2])
            elif bus_support_stops_count[bus.name] == 2:
                ids = [
                    id for id in range(len(bus_stops))
                    if bus_stops[id] in support_stops
                ]
                assert len(ids) == 3
                if ids[1] - ids[0] > ids[2] - ids[1]:
                    id = (ids[1] - ids[0]) // 2
                else:
                    id = (ids[2] - ids[1]) // 2 + ids[1]
                support_stops.add(bus_stops[id])
        else:
            support_stops.add(bus_stops[0])
            support_stops.add(bus_stops[-1])
    return support_stops


def interpolation(support_stops: typing.Set[str]) -> typing.Tuple:
    buses = MapBus.objects.all()

    res_x = {}
    res_y = {}

    for stop_sup_name in support_stops:
        stop_sup = Stop.objects.get(name=stop_sup_name)
        res_x[stop_sup.latitude] = stop_sup.name
        res_y[stop_sup.longitude] = stop_sup.name

    for bus in buses:
        stops = bus.stops
        prev_stop = Stop.objects.get(name=stops[0])
        prev_id = 0

        for id in range(1, len(stops)):
            if stops[id] in support_stops:
                cur_stop = Stop.objects.get(name=stops[id])

                x_step = (cur_stop.latitude - prev_stop.latitude) / (id - prev_id)
                y_step = (cur_stop.longitude - prev_stop.longitude) / (id - prev_id)

                for inter_id in range(prev_id + 1, id):
                    mul = inter_id - prev_id
                    lat = round(prev_stop.latitude + mul*x_step, 6)
                    lon = round(prev_stop.longitude + mul*y_step, 6)

                    res_x[lat] = stops[inter_id]
                    res_y[lon] = stops[inter_id]

                prev_stop = cur_stop
                prev_id = id
    return OrderedDict(sorted(res_x.items())), OrderedDict(sorted(res_y.items()))


def set_neighboors() -> typing.Dict[str, typing.Set[str]]:
    buses = MapBus.objects.all()

    res = defaultdict(set)
    for bus in buses:
        stops = bus.stops
        for i in range(1, len(stops)):
            stop_1 = stops[i - 1]
            stop_2 = stops[i]

            res[stop_1].add(stop_2)
            res[stop_2].add(stop_1)
    return res
