# class ApiRoute(APIView):

#     def get(self, request):
#         stop_from = get_object_or_404(
#             Stop, name=request.GET['from'], msg='Cant find stop_from',
#         )
#         stop_to = get_object_or_404(
#             Stop, name=request.GET['to'], msg='Cant find stop_to',
#         )
#         res = router_wrapper.build_path(
#             vertex_from_id=stop_from.in_id, vertex_to_id=stop_to.in_id,
#         )
#         if res is None:
#             return Response(
#                 {'error_msg': 'Stops are not connected'},
#                 status=status.HTTP_404_NOT_FOUND,
#             )
#         weight, route = res
#         serializer = RoutePartSerializer(route, many=True)
#         return Response(
#             {'total_time': float(f'{weight:.6f}'), 'items': serializer.data},
#             status=status.HTTP_200_OK,
#         )
