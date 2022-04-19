import pytest


class TestGetAPI:

    @pytest.mark.parametrize(
        'name, expected_bus',
        [
            pytest.param(
                '297',
                {
                    'stop_count': 6,
                    'route_length': 5880,
                    'unique_stop_count': 5,
                },
            ),
            pytest.param(
                '750',
                {
                    'stop_count': 2,
                    'route_length': 27600,
                    'unique_stop_count': 2,
                },
            ),
            pytest.param(
                '635',
                {
                    'stop_count': 11,
                    'route_length': 14810,
                    'unique_stop_count': 6,
                },
            ),
        ],
    )
    @pytest.mark.django_db(transaction=True)
    def test_correct_get(self, client, response_buses, name, expected_bus):
        response = client.get(f'/api/buses/?name={name}')

        assert response.status_code == 200
        assert response.json() == expected_bus
