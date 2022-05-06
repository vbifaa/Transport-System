import pytest

from routing.models import RoutePart
from transport.models import Bus, BusStop

from ..mocks import mock_router


class TestPostAPI:

    @mock_router
    @pytest.mark.parametrize(
        'data, expected_bus',
        [
            pytest.param(
                {
                    'name': '297',
                    'stops': [
                        'Biryulyovo Zapadnoye',
                        'Biryulyovo Tovarnaya',
                        'Universam',
                        'Biryusinka',
                        'Apteka',
                        'Biryulyovo Zapadnoye',
                    ],
                    'velocity': 50,
                    'is_roundtrip': True,
                },
                {
                    'name': '297',
                    'stop_count': 6,
                    'route_length': 5880,
                    'unique_stop_count': 5,
                },
                id='round_bus',
            ),
            pytest.param(
                {
                    'name': '750',
                    'stops': [
                        'Tolstopaltsevo',
                        'Rasskazovka',
                    ],
                    'velocity': 40,
                    'is_roundtrip': False,
                },
                {
                    'name': '750',
                    'velocity': 40,
                    'stop_count': 3,
                    'route_length': 27600,
                    'unique_stop_count': 2,
                },
                id='not_round_bus',
            ),
            pytest.param(
                {
                    'name': '635',
                    'stops': [
                        'Biryulyovo Tovarnaya',
                        'Universam',
                        'Biryusinka',
                        'TETs 26',
                        'Pokrovskaya',
                        'Prazhskaya',
                    ],
                    'velocity': 35,
                    'is_roundtrip': False,
                },
                {
                    'name': '635',
                    'velocity': 35,
                    'stop_count': 11,
                    'route_length': 14810,
                    'unique_stop_count': 6,
                },
                id='not_round_bus_not_same_return_trip',
            ),
        ],
    )
    @pytest.mark.django_db(transaction=True)
    def test_correct_post(
        self, client, router_wrapper_with_stops_only, data, expected_bus,
    ):
        assert len(RoutePart.objects.all()) == 11

        response = client.post('/api/buses/', data=data)

        assert response.status_code == 201
        assert len(Bus.objects.all()) == 1

        bus = Bus.objects.all()[0]
        assert bus.name == expected_bus['name']
        assert bus.stop_count == expected_bus['stop_count']
        assert bus.route_length == expected_bus['route_length']
        assert bus.unique_stop_count == expected_bus['unique_stop_count']

        assert len(BusStop.objects.all()) == len(set(data['stops']))
        for stop_name in data['stops']:
            assert BusStop.objects.filter(
                stop__name=stop_name, bus__name=data['name'],
            ).exists()

        st_n = len(data['stops'])
        print(st_n)
        expected_rp_count = (st_n * (st_n - 1)) // 2
        if not data['is_roundtrip']:
            expected_rp_count *= 2
        assert len(RoutePart.objects.all()) == expected_rp_count + 11

    @mock_router
    @pytest.mark.parametrize(
        'data, expceted_phrase',
        [
            pytest.param(
                {
                    'name': '297',
                    'velocity': 20,
                    'stops': [],
                    'is_roundtrip': True,
                },
                'This field is required.',
                id='zero',
            ),
            pytest.param(
                {
                    'name': '750',
                    'velocity': 20,
                    'stops': ['Tolstopaltsevo'],
                    'is_roundtrip': False,
                },
                'Кол-во остановок должно быть более одной',
                id='one',
            ),
            pytest.param(
                {
                    'name': '635',
                    'velocity': 22,
                    'stops': ['Pokrovskaya', 'Pokrovskaya'],
                    'is_roundtrip': True,
                },
                'Кол-во остановок должно быть более одной',
                id='two_but_round',
            ),
        ],
    )
    @pytest.mark.django_db(transaction=True)
    def test_few_stops(self, client, stops, data, expceted_phrase):
        response = client.post('/api/buses/', data=data)

        assert response.status_code == 400
        assert response.json() == {
            'stops': [expceted_phrase],
        }
        assert len(Bus.objects.all()) == 0

    @mock_router
    @pytest.mark.django_db(transaction=True)
    def test_round_last_stop_not_equal_first(self, client, stops):
        data = {
            'name': '635',
            'stops': [
                'Biryulyovo Tovarnaya',
                'Universam',
                'Biryusinka',
                'Prazhskaya',
            ],
            'velocity': 24,
            'is_roundtrip': True,
        }
        response = client.post('/api/buses/', data=data)

        assert response.status_code == 400
        assert response.json() == {
            'stops': [
                'В кольцевом маршруте начальная и '
                'конечная остановка должны быть равны',
            ],
        }
        assert len(Bus.objects.all()) == 0

    @mock_router
    @pytest.mark.django_db(transaction=True)
    def test_long_name(self, client, stops):
        data = {
            'name': '12345678901234567890123456',
            'velocity': 46,
            'stops': ['Biryulyovo Tovarnaya', 'Universam'],
            'is_roundtrip': False,
        }
        response = client.post('/api/buses/', data=data)

        assert response.status_code == 400
        assert 'name' in response.json()
        assert len(Bus.objects.all()) == 0
