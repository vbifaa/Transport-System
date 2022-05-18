import pytest

from tests.mocks import mock_dwg, mock_router


class TestGetMap:

    @mock_dwg
    @pytest.mark.django_db(transaction=True)
    def test_empty_map(self, client):
        response = client.get('/api/map/')

        assert response.status_code == 200
        assert response.content.decode('utf-8') == (
            '<svg baseProfile="full" height="100%" version="1.1" '
            'width="100%" xmlns="http://www.w3.org/2000/svg" '
            'xmlns:ev="http://www.w3.org/2001/xml-events" '
            'xmlns:xlink="http://www.w3.org/1999/xlink"><defs /></svg>'
        )


class TestGetRouteMap:

    @mock_dwg
    @mock_router
    @pytest.mark.django_db(transaction=True)
    def test_simple_call(self, client, router_wrapper, map_buses, load_file):
        response = client.get('/api/map/route/?from=Universam&to=Biryusinka')

        assert response.status_code == 200
        assert response.content.decode('utf-8') == load_file(
            'test_simple_call.svg',
        )
