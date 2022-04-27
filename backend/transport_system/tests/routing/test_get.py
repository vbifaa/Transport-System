import pytest

from ..mocks import mock_router


class TestGetAPI:

    @mock_router
    @pytest.mark.django_db(transaction=True)
    def test_correct_one_bus(self, client, router_wrapper):
        response = client.get('/api/route/?from=Universam&to=Biryusinka')

        assert response.status_code == 200
        assert response.json() == {
            'total_time': 6.14,
            'items': [
                {'type': 'WAIT', 'stop_name': 'Universam', 'time': 5},
                {
                    'type': 'BUS',
                    'bus': '635',
                    'span_count': 1,
                    'time': 1.14,
                },
            ],
        }

    @mock_router
    @pytest.mark.django_db(transaction=True)
    def test_correct_many_buses(self, client, router_wrapper):
        response = client.get(
            '/api/route/?from=Rossoshanskaya ulitsa&to=Biryulyovo Tovarnaya',
        )

        assert response.status_code == 200
        assert response.json() == {
            'total_time': 20.575,
            'items': [
                {
                    'stop_name': 'Rossoshanskaya ulitsa',
                    'time': 5.0,
                    'type': 'WAIT',
                },
                {'bus': '828', 'span_count': 2, 'time': 8.505, 'type': 'BUS'},
                {'stop_name': 'Universam', 'time': 5.0, 'type': 'WAIT'},
                {'bus': '635', 'span_count': 1, 'time': 2.07, 'type': 'BUS'},
            ],
        }

    @mock_router
    @pytest.mark.django_db(transaction=True)
    def test_no_path(self, client, router_wrapper):
        response = client.get('/api/route/?from=Universam&to=Rasskazovka')

        assert response.status_code == 404
        assert response.json() == {'error_msg': 'Stops are not connected'}
