import pytest

from transport.models import Stop


class TestPostAPI:

    @pytest.mark.django_db(transaction=True)
    def test_correct_post_stop(self, client):
        data = {
            'name': 'Astankino', 'longitude': 32.34698, 'latitude': 76.92813,
        }
        response = client.post('/api/stops/', data=data)

        assert response.status_code == 201
        assert len(Stop.objects.all()) == 1

        obj = Stop.objects.all()[0]
        assert data['name'] == obj.name
        assert data['latitude'] == obj.latitude
        assert data['longitude'] == obj.longitude

    @pytest.mark.django_db(transaction=True)
    def test_post_stop_long_name(self, client):
        name = '12345678901234567890123456'
        data = {'name': name, 'longitude': 32.34698, 'latitude': 76.92813}
        response = client.post('/api/stops/', data=data)

        assert response.status_code == 400
        assert len(Stop.objects.all()) == 0
        assert 'name' in response.json()

    @pytest.mark.django_db(transaction=True)
    def test_post_stop_with_exist_name(self, client):
        Stop.objects.create(name='Fulk', latitude=0, longitude=0)

        data = {'name': 'Fulk', 'longitude': 32.34698, 'latitude': 76.92813}
        response = client.post('/api/stops/', data=data)

        assert response.status_code == 400
        assert len(Stop.objects.all()) == 1
        assert 'name' in response.json()
