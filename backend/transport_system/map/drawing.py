import typing

import svgwrite
from PIL import ImageColor

from .models import MapBus, MapStop

MAP_SETTINGS = {
    'width': 1200,
    'height': 500,
    'padding': 50,
    'outer_margin': 150,
    'stop_radius': 5,
    'line_width': 14,
    'bus_label_font_size': 20,
    'stop_label_font_size': 18,
    'stop_label_offset': (7, -3),
    'underlayer_color': (255, 255, 255),
    'underlayer_width': 3,
    'bus_label_font_size': 20,
    'bus_label_offset': (7, 15),
}


def draw_map(max_x_map_id: int, max_y_map_id: int, dwg: svgwrite.Drawing):
    buses = MapBus.objects.all()
    stops = MapStop.objects.all()

    stops_coord = {}
    for stop in stops:
        stops_coord[stop.name] = get_coord_from_id(
            x_id=stop.x_map_id,
            y_id=stop.y_map_id,
            max_x_map_id=max_x_map_id,
            max_y_map_id=max_y_map_id,
        )

    for bus in buses:
        draw_way(dwg=dwg, stops_coord=stops_coord, bus=bus)

    for _, coord in stops_coord.items():
        draw_station_circle(dwg=dwg, coord=coord)

    for stop_name, coord in stops_coord.items():
        draw_station_title(dwg=dwg, stop_name=stop_name, coord=coord)

    for bus in buses:
        draw_bus_title(dwg=dwg, stops_coord=stops_coord, bus=bus)

    dwg.save()


def get_coord_from_id(
    x_id: int, y_id: int, max_x_map_id: int, max_y_map_id: int,
) -> typing.Tuple[int, int]:
    y_step = 0
    if max_y_map_id > 0:
        y_step = (
            MAP_SETTINGS['height'] - 2 * MAP_SETTINGS['padding']
        ) / max_y_map_id
    x_step = 0
    if max_x_map_id > 0:
        x_step = (
            MAP_SETTINGS['width'] - 2 * MAP_SETTINGS['padding']
        ) / max_x_map_id
    x = x_id * x_step + MAP_SETTINGS['padding']
    y = (
        MAP_SETTINGS['height'] - MAP_SETTINGS['padding']
    ) - (y_id * y_step)
    return round(x, 3), round(y, 3)


def draw_way(dwg: svgwrite.Drawing, stops_coord: dict, bus):
    line = [stops_coord[stop_name] for stop_name in bus.stops]
    polyline = svgwrite.shapes.Polyline(
        points=line,
        stroke=svgwrite.rgb(*ImageColor.getcolor(bus.color, 'RGB'), 'RGB'),
        stroke_width=MAP_SETTINGS['line_width'],
        stroke_linecap='round',
        stroke_linejoin='round',
        fill='none',
    )
    dwg.add(polyline)


def draw_bus_title(dwg: svgwrite.Drawing, stops_coord: dict, bus):
    print(bus.name)
    bus_stops_coord = [stops_coord[bus.stops[0]]]
    if bus.type == 'BACKWARD':
        bus_stops_coord.append(stops_coord[bus.stops[-1]])

    common_settings = {
        'dx': [MAP_SETTINGS['bus_label_offset'][0]],
        'dy': [MAP_SETTINGS['bus_label_offset'][1]],
        'font_family': 'Verdana',
        'font_weight': 'bold',
        'font_size': MAP_SETTINGS['bus_label_font_size'],
    }
    for coord in bus_stops_coord:
        common_settings['x'] = coord[0],
        common_settings['y'] = coord[1],

        under_text = svgwrite.text.Text(
            bus.name,
            fill=svgwrite.rgb(*MAP_SETTINGS['underlayer_color'], 'RGB'),
            stroke=svgwrite.rgb(*MAP_SETTINGS['underlayer_color'], 'RGB'),
            stroke_width=MAP_SETTINGS['underlayer_width'],
            stroke_linecap='round',
            stroke_linejoin='round',
            **common_settings,
        )
        text = svgwrite.text.Text(
            bus.name,
            fill=svgwrite.rgb(*ImageColor.getcolor(bus.color, 'RGB'), 'RGB'),
            **common_settings,
        )
        dwg.add(under_text)
        dwg.add(text)


def draw_station_circle(dwg: svgwrite.Drawing, coord: tuple):
    circle = svgwrite.shapes.Circle(
        center=coord,
        r=MAP_SETTINGS['stop_radius'],
        fill=svgwrite.rgb(255, 255, 255, 'RGB'),
    )
    dwg.add(circle)


def draw_station_title(dwg: svgwrite.Drawing, stop_name: str, coord: tuple):
    common_settings = {
        'x': [coord[0]],
        'y': [coord[1]],
        'dx': [MAP_SETTINGS['stop_label_offset'][0]],
        'dy': [MAP_SETTINGS['stop_label_offset'][1]],
        'font_family': 'Verdana',
        'font_size': MAP_SETTINGS['stop_label_font_size'],
    }
    under_text = svgwrite.text.Text(
        stop_name,
        fill=svgwrite.rgb(*MAP_SETTINGS['underlayer_color'], 'RGB'),
        stroke=svgwrite.rgb(*MAP_SETTINGS['underlayer_color'], 'RGB'),
        stroke_width=MAP_SETTINGS['underlayer_width'],
        stroke_linecap='round',
        stroke_linejoin='round',
        **common_settings,
    )
    text = svgwrite.text.Text(
        stop_name,
        fill=svgwrite.rgb(0, 0, 0, 'RGB'),
        **common_settings,
    )
    dwg.add(under_text)
    dwg.add(text)
