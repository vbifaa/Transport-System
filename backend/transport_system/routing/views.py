# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# from .models import graph


# class ApiGraph(APIView):
#     def get(self, request):
#         return Response({'edges': graph.edges}, status=status.HTTP_200_OK)

#     def post(self, request):
#         graph.add_edge(request.POST.getlist('edge'))
#         return Response(status=status.HTTP_201_CREATED)
