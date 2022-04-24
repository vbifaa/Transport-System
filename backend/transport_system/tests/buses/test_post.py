import pytest

from transport.models import Bus, BusStop


class TestPostAPI:

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
    def test_correct_post(self, client, stops, data, expected_bus):
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

    @pytest.mark.parametrize(
        'data',
        [
            pytest.param(
                {'name': '297', 'velocity': 20, 'stops': [], 'is_roundtrip': True},
                id='zero',
            ),
            pytest.param(
                {
                    'name': '750',
                    'velocity': 20,
                    'stops': ['Tolstopaltsevo'],
                    'is_roundtrip': False,
                },
                id='one',
            ),
            pytest.param(
                {
                    'name': '635',
                    'velocity': 22,
                    'stops': ['Pokrovskaya', 'Pokrovskaya'],
                    'is_roundtrip': True,
                },
                id='two_but_round',
            ),
        ],
    )
    @pytest.mark.django_db(transaction=True)
    def test_few_stops(self, client, stops, data):
        response = client.post('/api/buses/', data=data)

        assert response.status_code == 400
        assert response.json() == {
            'stops': ['Кол-во остановок должно быть более одной'],
        }
        assert len(Bus.objects.all()) == 0

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
