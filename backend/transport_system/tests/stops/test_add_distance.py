import pytest

from transport.models import Stop, StopDistance


class TestPostAPI:

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_no_from_stop(self, client):
        Stop.objects.create(name='2', latitude=0, longitude=0)

        data = {'from_stop': '1', 'to_stop': '2', 'distance': 20}
        response = client.post('/api/stops/add_distance/', data=data)

        assert response.status_code == 404
        assert len(StopDistance.objects.all()) == 0

    @pytest.mark.django_db(transaction=True)
    def test_no_to_stop(self, client):
        Stop.objects.create(name='1', latitude=0, longitude=0)

        data = {'from_stop': '1', 'to_stop': '2', 'distance': 20}
        response = client.post('/api/stops/add_distance/', data=data)

        assert response.status_code == 404
        assert len(StopDistance.objects.all()) == 0

    @pytest.mark.django_db(transaction=True)
    def test_zero_distance(self, client):
        Stop.objects.create(name='1', latitude=0, longitude=0)
        Stop.objects.create(name='2', latitude=0, longitude=0)

        data = {'from_stop': '1', 'to_stop': '2', 'distance': 0}
        response = client.post('/api/stops/add_distance/', data=data)

        assert response.status_code == 400
        assert 'distance' in response.json()
        assert len(StopDistance.objects.all()) == 0

    @pytest.mark.django_db(transaction=True)
    def test_distance_less_than_real_distance(self, client):
        Stop.objects.create(name='1', latitude=24.34627, longitude=56.25103)
        Stop.objects.create(name='2', latitude=24.33614, longitude=56.28245)

        data = {'from_stop': '1', 'to_stop': '2', 'distance': 336}
        response = client.post('/api/stops/add_distance/', data=data)

        assert response.status_code == 400
        assert 'distance' in response.json()
        assert response.json()['distance'] == [
            'Расстояние должно быть больше реального. '
            'Реальное: 3377. Было введено: 336.'
        ]
        assert len(StopDistance.objects.all()) == 0

    @pytest.mark.django_db(transaction=True)
    def test_distance_correct_stop_distance(self, client):
        Stop.objects.create(name='1', latitude=24.34627, longitude=56.25103)
        Stop.objects.create(name='2', latitude=24.33614, longitude=56.28245)

        data = {'from_stop': '1', 'to_stop': '2', 'distance': 3377}
        response = client.post('/api/stops/add_distance/', data=data)

        assert response.status_code == 201
        assert len(StopDistance.objects.all()) == 1

        obj = StopDistance.objects.all()[0]
        assert data['from_stop'] == obj.from_stop.name
        assert data['to_stop'] == obj.to_stop.name
        assert data['distance'] == obj.distance
