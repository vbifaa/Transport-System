import pytest

from transport.models import Bus, BusStop, Stop


class TestGetAPI:

    @pytest.mark.django_db(transaction=True)
    def test_correct_one_bus(self, client):
        Stop.objects.create(name='Astankino', latitude=0, longitude=0)
        Bus.objects.create(
            name='123',
            velocity=47,
            route_length=1,
            stop_count=1,
            unique_stop_count=1,
        )
        BusStop.objects.create(
            stop=Stop.objects.all()[0], bus=Bus.objects.all()[0],
        )

        response = client.get('/api/stops/?name=Astankino')

        assert response.status_code == 200
        assert response.json() == {'buses': ['123']}

    @pytest.mark.django_db(transaction=True)
    def test_correct_two_buses(self, client):
        for i in range(0, 4):
            Stop.objects.create(
                name='Astankino' + str(i), latitude=0, longitude=0,
            )

        Bus.objects.create(
            name='123',
            velocity=40,
            route_length=1,
            stop_count=1,
            unique_stop_count=1,
        )
        Bus.objects.create(
            name='374',
            velocity=35,
            route_length=1,
            stop_count=1,
            unique_stop_count=1,
        )

        for i in range(0, 3):
            BusStop.objects.create(
                stop=Stop.objects.get(name='Astankino' + str(i)),
                bus=Bus.objects.get(name='123'),
            )
        for i in range(1, 4):
            BusStop.objects.create(
                stop=Stop.objects.get(name='Astankino' + str(i)),
                bus=Bus.objects.get(name='374'),
            )

        response = client.get('/api/stops/?name=Astankino0')
        assert response.status_code == 200
        assert response.json() == {'buses': ['123']}

        response = client.get('/api/stops/?name=Astankino1')
        assert response.status_code == 200
        assert response.json() == {'buses': ['123', '374']}

        response = client.get('/api/stops/?name=Astankino3')
        assert response.status_code == 200
        assert response.json() == {'buses': ['374']}
