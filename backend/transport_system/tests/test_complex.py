import pytest

from .mocks import mock_router


class TestAllAPI:

    @mock_router
    @pytest.mark.parametrize(
        'file_path',
        [pytest.param('scenario_1.json')],
    )
    @pytest.mark.django_db(transaction=True)
    def test_all_api(self, client, load_json, file_path):
        scenario = load_json(file_path)

        for block in scenario:
            request = block['request']
            if request['type'] == 'POST':
                response = client.post(request['url'], data=request['data'])
            else:
                response = client.get(request['url'], data=request['data'])
            expected_response = block['response']
            
            assert expected_response['code'] == response.status_code, request
            if expected_response.get('json'):
                assert expected_response['json'] == response.json()
