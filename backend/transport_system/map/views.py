import json
import typing
from dataclasses import dataclass

import svgwrite
from django.http import HttpResponse
from rest_framework.decorators import api_view

from routing.views import route

from .drawing import draw_map, draw_route
from .gluing import gluing
from .models import MapBus


@dataclass
class DrawSettings:
    dwg: typing.Optional[svgwrite.Drawing] = None
    max_x_map_id: int = 0
    max_y_map_id: int = 0


settings = DrawSettings()


@api_view(['get'])
def map(request):
    if settings.dwg is None:
        settings.dwg = svgwrite.Drawing()
        settings.max_x_map_id, settings.max_y_map_id = gluing()
        draw_map(
            max_x_map_id=settings.max_x_map_id,
            max_y_map_id=settings.max_y_map_id,
            dwg=settings.dwg,
        )
        settings.map_build = True

    return HttpResponse(settings.dwg.tostring(), content_type='image/svg+xml')


@api_view(['get'])
def map_route(request):
    if not settings.dwg:
        response = map(request._request)
        if response.status_code != 200:
            return response

    response = route(request._request)
    if response.status_code != 200:
        return response
    res = json.loads(response.rendered_content.decode('utf-8'))

    map_route = convert_to_map_route(
        route=res['items'], to_st=request.GET['to'],
    )
    draw_route(
        route=map_route,
        max_x_map_id=settings.max_x_map_id,
        max_y_map_id=settings.max_y_map_id,
        dwg=settings.dwg,
    )
    return HttpResponse(settings.dwg.tostring(), content_type='image/svg+xml')


def convert_to_map_route(route: list, to_st: str) -> list:
    assert len(route) % 2 == 0
    print(route)

    res = []
    for id in range(len(route) // 2):
        from_st_name = route[2*id]['stop_name']
        to_st_name = (
            route[2*id + 2]['stop_name']
            if 2*id + 2 < len(route) else to_st
        )
        bus_name = route[2*id + 1]['bus']

        bus = MapBus.objects.get(name=bus_name)

        start_st_id = bus.stops.index(from_st_name)
        end_st_id = bus.stops.index(to_st_name)

        step = 1
        if end_st_id < start_st_id:
            step = -1

        map_stops = []
        for st_id in range(start_st_id, end_st_id + step, step):
            map_stops.append(bus.stops[st_id])

        res.append({'color': bus.color, 'stops': map_stops})
    return res
