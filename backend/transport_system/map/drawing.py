import svgwrite

from .gluing import MAX_X_MAP_ID, MAX_Y_MAP_ID
from .models import MapBus, MapStop

FILE_PATH = 'db.svg'
MAP_WRITED = False


def draw_map():
    dwg = svgwrite.Drawing(FILE_PATH)

    draw_ways(dwg)
    draw_bus_title()
    draw_stations()
    draw_station_title()

    dwg.save()
    MAP_WRITED = True

def draw_ways(dwg: svgwrite.Drawing):
    buses = MapBus.objects.all()

    for bus in buses:
        polyline = svgwrite.shapes.Polyline()

def draw_bus_title():
    pass
def draw_stations():
    pass
def draw_station_title():
    pass

