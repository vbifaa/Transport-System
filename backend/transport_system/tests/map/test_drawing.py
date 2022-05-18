import pytest
import svgwrite

from map.drawing import MAP_SETTINGS, draw_map, get_coord_from_id

MAX_Y = MAP_SETTINGS['height'] - MAP_SETTINGS['padding']
MIN_X = MAP_SETTINGS['padding']


class TestCoordinates:

    @pytest.mark.parametrize(
        'data, expected_res',
        [
            pytest.param(
                {"x_id": 0, 'y_id': 0, 'max_x_map_id': 0, 'max_y_map_id': 0},
                (MIN_X, MAX_Y),
                id='One point'
            ),
        ],
    )
    def test_get_coord_from_id(self, data, expected_res):
        res = get_coord_from_id(**data)
        assert res == expected_res


# check that complete successful
class TestDraw:

    @pytest.mark.django_db(transaction=True)
    def test_draw_map(self, map_gluing):
        dwg = svgwrite.Drawing()
        x_id, y_id = map_gluing
        draw_map(max_x_map_id=x_id, max_y_map_id=y_id, dwg=dwg)
