import pytest

from .mocks import mock_dwg, mock_router


class TestAllAPI:

    @mock_dwg
    @mock_router
    @pytest.mark.parametrize(
        'file_path',
        [
            pytest.param('scenario_1.json'),
            pytest.param('scenario_2.json'),
        ],
    )
    @pytest.mark.django_db(transaction=True)
    def test_all_api(self, client, load_json, file_path):
        scenario = load_json(file_path)

        for block in scenario:
            request = block['request']
            url = request['url']
            if request['type'] == 'POST':
                response = client.post(url, data=request.get('data'))
            else:
                response = client.get(url, data=request.get('data'))
            expected_response = block['response']

            assert expected_response['code'] == response.status_code

            if 'json' in expected_response:
                assert expected_response['json'] == response.json()
            if 'content' in expected_response:
                assert expected_response[
                    'content'
                ] == response.content.decode('utf-8'), url
