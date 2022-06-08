import pytest

from routing.models import Graph, GraphEdge, RoutePart, RouterWrapper
from transport.models import Stop


class TestRouterWrapper:

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_add_stop(self):
        router_wrapper = RouterWrapper(Graph())
        stop_name = 'Astankino'
        Stop.objects.create(
            name=stop_name, longitude=0.0, latitude=0.0,
        )

        assert len(RoutePart.objects.all()) == 0

        router_wrapper.add_stop(stop_name)
        assert GraphEdge.objects.count() == 1
        obj = GraphEdge.objects.all()[0]

        assert obj.from_v == 0
        assert obj.to_v == 1
        assert obj.weight == 5

        assert router_wrapper.router is None

        assert len(RoutePart.objects.all()) == 1
        route_part = RoutePart.objects.all()[0]
        assert route_part.type == RoutePart.RoutePartType.WAIT
        assert route_part.name == stop_name
        assert route_part.time == 5.0
        assert route_part.span_count == 1

    @pytest.mark.parametrize(
        'from_stop, to_stop, expected_data',
        [
            pytest.param(
                'Biryulyovo Zapadnoye',
                'Biryusinka',
                {'name': '297', 'time': 6.375, 'span_count': 3},
                id='Biryulyovo Zapadnoye->Biryusinka',
            ),
            pytest.param(
                'Biryulyovo Tovarnaya',
                'Apteka',
                {'name': '297', 'time': 2.79, 'span_count': 3},
                id='Biryulyovo Tovarnaya->Apteka',
            ),
            pytest.param(
                'Universam',
                'Biryusinka',
                {'name': '297', 'time': 1.14, 'span_count': 1},
                id='Universam->Biryusinka',
            ),
            pytest.param(
                'Biryulyovo Tovarnaya',
                'Biryulyovo Zapadnoye',
                {'name': '297', 'time': 4.92, 'span_count': 4},
                id='Biryulyovo Tovarnaya->Biryulyovo Zapadnoye',
            ),
            pytest.param(
                'Biryulyovo Zapadnoye',
                'Biryulyovo Zapadnoye',
                {'name': '297', 'time': 8.82, 'span_count': 5},
                id='Biryulyovo Zapadnoye->Biryulyovo Zapadnoye',
            ),
        ],
    )
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_add_not_round_bus(
        self,
        response_buses,
        router_wrapper_with_stops_only: RouterWrapper,
        from_stop,
        to_stop,
        expected_data,
    ):
        assert len(RoutePart.objects.all()) == 11

        bus_name = '297'
        router_wrapper_with_stops_only.add_bus(
            bus_name=bus_name,
            stops=[
                'Biryulyovo Zapadnoye',
                'Biryulyovo Tovarnaya',
                'Universam',
                'Biryusinka',
                'Apteka',
                'Biryulyovo Zapadnoye',
            ],
            one_direction=True,
        )
        assert len(RoutePart.objects.all()) == 26
        route_parts = RoutePart.objects.filter(
            type=RoutePart.RoutePartType.BUS, name=bus_name,
        )
        assert len(route_parts) == 15
        assert router_wrapper_with_stops_only.router is None

        self.assert_edge(
            from_stop=from_stop,
            to_stop=to_stop,
            expected_data=expected_data,
            r_graph=router_wrapper_with_stops_only.graph,
        )

    @pytest.mark.parametrize(
        'from_stop, to_stop, expected_data',
        [
            pytest.param(
                'Biryulyovo Tovarnaya',
                'Biryusinka',
                {'name': '635', 'time': 2.475, 'span_count': 2},
                id='Biryulyovo Tovarnaya->Biryusinka',
            ),
            pytest.param(
                'Universam',
                'Prazhskaya',
                {'name': '635', 'time': 9.405, 'span_count': 4},
                id='Universam->Prazhskaya',
            ),
            pytest.param(
                'Biryusinka',
                'Biryulyovo Tovarnaya',
                {'name': '635', 'time': 3.21, 'span_count': 2},
                id='Biryusinka->Biryulyovo Tovarnaya',
            ),
            pytest.param(
                'Pokrovskaya',
                'TETs 26',
                {'name': '635', 'time': 4.275, 'span_count': 1},
                id='Pokrovskaya->TETs 26',
            ),
            pytest.param(
                'Prazhskaya',
                'Biryulyovo Tovarnaya',
                {'name': '635', 'time': 11.475, 'span_count': 5},
                id='Prazhskaya->Biryulyovo Tovarnaya',
            ),
        ],
    )
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_add_round_bus(
        self,
        response_buses,
        router_wrapper_with_stops_only: RouterWrapper,
        from_stop,
        to_stop,
        expected_data,
    ):
        assert len(RoutePart.objects.all()) == 11

        bus_name = '635'
        router_wrapper_with_stops_only.add_bus(
            bus_name=bus_name,
            stops=[
                'Biryulyovo Tovarnaya',
                'Universam',
                'Biryusinka',
                'TETs 26',
                'Pokrovskaya',
                'Prazhskaya'
            ],
            one_direction=False,
        )
        assert len(RoutePart.objects.all()) == 41
        route_parts = RoutePart.objects.filter(
            type=RoutePart.RoutePartType.BUS, name=bus_name,
        )
        assert len(route_parts) == 30
        assert router_wrapper_with_stops_only.router is None

        self.assert_edge(
            from_stop=from_stop,
            to_stop=to_stop,
            expected_data=expected_data,
            r_graph=router_wrapper_with_stops_only.graph,
        )

    def assert_edge(self, from_stop, to_stop, expected_data, r_graph):
        from_id = Stop.objects.get(name=from_stop).out_id
        to_id = Stop.objects.get(name=to_stop).in_id

        edge_id = -1
        for edge in r_graph.get_incident_edges(from_id):
            if edge.to_v == to_id:
                edge_id = edge.id
                break
        assert edge_id != -1

        g_edge = r_graph.get_edge(edge_id)
        rp_edge = RoutePart.objects.get(id=edge_id)

        assert pytest.approx(g_edge.weight) == expected_data['time']
        assert pytest.approx(rp_edge.time) == expected_data['time']
        assert rp_edge.name == expected_data['name']
        assert rp_edge.span_count == expected_data['span_count']

    @pytest.mark.parametrize(
        'from_stop, to_stop, expected_weight, expected_data',
        [
            pytest.param(
                'Biryulyovo Zapadnoye',
                'Biryulyovo Tovarnaya',
                8.9,
                [{'type': 'Bus', 'name': '297', 'time': 3.9, 'span_count': 1}],
                id='One_bus_Biryulyovo Tovarnaya->Biryusinka',
            ),
            pytest.param(
                'Tolstopaltsevo',
                'Rasskazovka',
                25.7,
                [
                    {
                        'type': 'Bus',
                        'name': '750',
                        'time': 20.7,
                        'span_count': 1,
                    },
                ],
                id='One_bus_Tolstopaltsevo->Rasskazovka',
            ),
            pytest.param(
                'Rossoshanskaya ulitsa',
                'Pokrovskaya',
                9.815,
                [
                    {
                        'type': 'Bus',
                        'name': '828',
                        'time': 4.815,
                        'span_count': 1,
                    },
                ],
                id='One_bus_Rossoshanskaya ulitsa->Pokrovskaya',
            ),
            pytest.param(
                'Biryulyovo Tovarnaya',
                'Prazhskaya',
                15.74,
                [
                    {
                        'type': 'Bus',
                        'name': '635',
                        'time': 10.74,
                        'span_count': 5,
                    },
                ],
                id='One_bus_Prazhskaya->Pokrovskaya',
            ),
            pytest.param(
                'Biryulyovo Zapadnoye',
                'Prazhskaya',
                19.315,
                [
                    {
                        'type': 'Bus',
                        'name': '828',
                        'time': 1.65,
                        'span_count': 1,
                    },
                    {'type': 'Wait', 'name': 'TETs 26', 'time': 5},
                    {
                        'type': 'Bus',
                        'name': '635',
                        'time': 7.665,
                        'span_count': 2,
                    },
                ],
                id='Many_buses_Biryulyovo Zapadnoye->Prazhskaya',
            ),
        ],
    )
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_build_path(
        self,
        router_wrapper: RouterWrapper,
        from_stop,
        to_stop,
        expected_weight,
        expected_data,
    ):
        assert router_wrapper.router is None

        expected_data.insert(
            0, {'type': 'Wait', 'name': from_stop, 'time': 5},
        )

        from_id = Stop.objects.get(name=from_stop).in_id
        to_id = Stop.objects.get(name=to_stop).in_id
        weight, data = router_wrapper.build_path(
            vertex_from_id=from_id, vertex_to_id=to_id,
        )
        assert router_wrapper.router is not None

        assert weight == expected_weight
        assert len(data) == len(expected_data)

        for i in range(len(data)):
            assert data[i].type == expected_data[i]['type'].upper()
            assert data[i].name == expected_data[i]['name']
            assert data[i].span_count == expected_data[i].get('span_count', 1)
            assert pytest.approx(data[i].time) == expected_data[i]['time']

    @pytest.mark.parametrize(
        'from_stop, to_stop',
        [
            pytest.param(
                'Biryulyovo Zapadnoye',
                'Tolstopaltsevo',
                id='Biryulyovo Tovarnaya->Tolstopaltsevo',
            ),
            pytest.param(
                'Prazhskaya', 'Rasskazovka', id='Prazhskaya->Rasskazovka',
            ),
        ],
    )
    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_no_path(self, from_stop, to_stop, router_wrapper):
        from_id = Stop.objects.get(name=from_stop).in_id
        to_id = Stop.objects.get(name=to_stop).in_id

        res = router_wrapper.build_path(
            vertex_from_id=from_id, vertex_to_id=to_id,
        )

        assert res is None
