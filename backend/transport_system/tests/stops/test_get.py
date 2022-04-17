# import pytest

# from stops.models import Stop


# class TestGetAPI:

#     @pytest.mark.django_db(transaction=True)
#     def test_correct_post_stop(self, client):
#         data = {
#             'name': 'Astankino',
#         }
#         response = client.get('/api/stops/', data=data)

#         assert response.status_code == 200
#         assert response.json() == ''
#         assert len(Stop.objects.all()) == 1

#         obj = Stop.objects.all()[0]
#         assert data['name'] == obj.name
#         assert data['latitude'] == obj.latitude
#         assert data['longitude'] == obj.longitude