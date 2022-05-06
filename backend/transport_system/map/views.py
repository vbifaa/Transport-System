import os

import svgwrite
from django.http import HttpResponse
from rest_framework.views import APIView

from map.drawing import draw_map
from map.gluing import gluing

MAP_BUILD = False
FILE_PATH = 'map/db.svg'


class ApiMap(APIView):

    def get(self, request):
        dwg = svgwrite.Drawing(FILE_PATH)
        print(FILE_PATH)
        global MAP_BUILD
        if not MAP_BUILD:
            try:  # if there are no db.svg it will throw exception
                script_dir = os.path.dirname(__file__)
                os.remove(os.path.join(script_dir, 'db.svg'))
            except Exception:
                pass

            x_id, y_id = gluing()
            draw_map(max_x_map_id=x_id, max_y_map_id=y_id, dwg=dwg)
            # MAP_BUILED = True
        return HttpResponse(dwg.tostring(), content_type='image/svg+xml')
