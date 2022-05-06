from typing import OrderedDict

import pytest

from map.gluing import gluing, interpolation, set_neighboors, set_support_stops
from map.models import MapStop
from transport.models import Stop


class TestSupportStops:

    @pytest.mark.django_db(transaction=True)
    def test_backward_no_round(self, backward_bus):
        res = set_support_stops()

        assert res == set(['Astankino', 'Kalugino'])

    @pytest.mark.django_db(transaction=True)
    def test_stop_without_buses(self, backward_bus):
        Stop.objects.create(name='name', longitude=3.4, latitude=4.3)
        res = set_support_stops()

        assert res == set(['Astankino', 'Kalugino', 'name'])

    @pytest.mark.django_db(transaction=True)
    def test_round_one_support(self, round_bus):
        res = set_support_stops()

        assert res == set(['AstankinoR', 'VazhinoR', 'KaluginoR'])

    @pytest.mark.django_db(transaction=True)
    def test_round_two_support(self, round_bus_two_support):
        res = set_support_stops()

        assert res == set(['Astankino', 'Vazhino', 'Kalugino', 'Lazino'])

    @pytest.mark.django_db(transaction=True)
    def test_round_three_support(self, round_bus_three_support):
        res = set_support_stops()

        assert res == set(
            ['Astankino', 'Vazhino', 'Vaznaya', 'Lazino', 'Lazino2'],
        )

    @pytest.mark.django_db(transaction=True)
    def test_massive(self, map_buses):
        res = set_support_stops()

        assert res == set(
            [
                'Tolstopaltsevo',
                'Rasskazovka',
                'Prazhskaya',
                'Rossoshanskaya ulitsa',
                'Pokrovskaya',
                'Universam',
                'Biryusinka',
                'TETs 26',
                'Biryulyovo Zapadnoye',
                'Biryulyovo Tovarnaya',
            ],
        )


class TestNeighboors:

    @pytest.mark.django_db(transaction=True)
    def test_round(self, round_bus):
        res = set_neighboors()

        assert res == {
            'AstankinoR': set(['VazhinoR', 'KaluginoR']),
            'VazhinoR': set(['AstankinoR', 'KaluginoR']),
            'KaluginoR': set(['VazhinoR', 'AstankinoR']),
        }

    @pytest.mark.django_db(transaction=True)
    def test_massive(self, map_buses):
        res = set_neighboors()

        assert res == {
            'Biryulyovo Zapadnoye': set(
                ['Apteka', 'Biryulyovo Tovarnaya', 'TETs 26'],
            ),
            'Universam': set(
                ['Pokrovskaya', 'Biryulyovo Tovarnaya', 'Biryusinka'],
            ),
            'Biryulyovo Tovarnaya': set(['Universam', 'Biryulyovo Zapadnoye']),
            'Biryusinka': set(['Universam', 'Apteka', 'TETs 26']),
            'Apteka': set(['Biryusinka', 'Biryulyovo Zapadnoye']),
            'TETs 26': set(
                ['Biryusinka', 'Biryulyovo Zapadnoye', 'Pokrovskaya'],
            ),
            'Pokrovskaya': set(
                [
                    'Rossoshanskaya ulitsa',
                    'Prazhskaya',
                    'Universam',
                    'TETs 26',
                ],
            ),
            'Rossoshanskaya ulitsa': set(['Pokrovskaya']),
            'Prazhskaya': set(['Pokrovskaya']),
            'Tolstopaltsevo': set(['Rasskazovka']),
            'Rasskazovka': set(['Tolstopaltsevo']),
        }


class TestInterpolation:

    @pytest.mark.django_db(transaction=True)
    def test_no_inter(self, map_stops_with_coordeinates):
        support_stops = set(['start', 'finish'])
        res_x, res_y = interpolation(support_stops)

        assert res_x == OrderedDict(
            {
                0.0: 'start',
                0.8: 'inter1',
                1.6: 'inter2',
                2.4: 'inter3',
                3.2: 'finish',
            }
        )
        assert res_y == OrderedDict(
            {
                0.0: 'start',
                1.25: 'inter1',
                2.5: 'inter2',
                3.75: 'inter3',
                5.0: 'finish',
            }
        )

    @pytest.mark.django_db(transaction=True)
    def test_with_stop_without_bus(self, map_stops_with_coordeinates):
        support_stops = set(['start', 'finish'])
        res_x, res_y = interpolation(support_stops)

        assert res_x == OrderedDict(
            {
                0.0: 'start',
                0.8: 'inter1',
                1.6: 'inter2',
                2.4: 'inter3',
                3.2: 'finish',
            }
        )
        assert res_y == OrderedDict(
            {
                0.0: 'start',
                1.25: 'inter1',
                2.5: 'inter2',
                3.75: 'inter3',
                5.0: 'finish',
            }
        )

    @pytest.mark.django_db(transaction=True)
    def test_one_inter(self, map_stops_with_coordeinates):
        support_stops = set(['start', 'inter2', 'finish'])
        res_x, res_y = interpolation(support_stops)

        assert res_x == OrderedDict(
            {
                0.0: 'start',
                2.3: 'inter1',
                3.2: 'finish',
                3.9: 'inter3',
                4.6: 'inter2',
            }
        )
        assert res_y == OrderedDict(
            {
                0.0: 'start',
                2.1: 'inter1',
                4.2: 'inter2',
                4.6: 'inter3',
                5.0: 'finish',
            }
        )

    @pytest.mark.django_db(transaction=True)
    def test_massive(self, map_buses, load_json):
        res_x, res_y = interpolation(support_stops=set_support_stops())

        stops = load_json('stops.json')
        excepted_x = {37.650045: 'Apteka'}
        excepted_y = {55.577718: 'Apteka'}
        for stop in stops:
            if stop['name'] != 'Apteka':
                excepted_x[stop['longitude']] = stop['name']
                excepted_y[stop['latitude']] = stop['name']

        assert res_x == OrderedDict(sorted(excepted_x.items()))
        assert res_y == OrderedDict(sorted(excepted_y.items()))


class TestGluing:

    @pytest.mark.django_db(transaction=True)
    def test_massive(self, map_buses):
        assert MapStop.objects.count() == 0
        res = gluing()
        assert res == (6, 5)

        assert MapStop.objects.count() == Stop.objects.count()
        res = {
            stop.name: (stop.x_map_id, stop.y_map_id)
            for stop in MapStop.objects.all()
        }
        expected = {
            'Biryulyovo Zapadnoye': (5, 0),
            'Apteka': (4, 1),
            'TETs 26': (2, 1),
            'Biryusinka': (3, 2),
            'Universam': (2, 3),
            'Biryulyovo Tovarnaya': (6, 4),
            'Rossoshanskaya ulitsa': (0, 0),
            'Pokrovskaya': (1, 4),
            'Tolstopaltsevo': (0, 1),
            'Prazhskaya': (0, 5),
            'Rasskazovka': (1, 5),
        }
        assert res == expected
