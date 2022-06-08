import pytest

from routing.models import Edge, Graph
from routing.models import RouteInternalData as E  # noqa: N814
from routing.models import Router


class TestRouter:

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_initialize_simple_graph(self, graph_1: Graph):
        router = Router(empty=True)
        assert router._routes_internal_data == []

        router._initialize(graph_1)
        assert router._routes_internal_data == [
            [E(0, None), E(5, 1)],
            [E(10, 2), E(0, None)],
        ]

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_initialize_complex_graph(self, graph_2: Graph):
        router = Router(empty=True)
        assert router._routes_internal_data == []

        router._initialize(graph_2)
        assert router._routes_internal_data == [
            [E(0, None), None, None, None, None],
            [None, E(0, None), E(10, 2), None, None],
            [None, None, E(0, None), E(15, 3), None],
            [None, E(20, 4), None, E(0, None), E(17, 5)],
            [None, E(40, 7), E(23, 6), None, E(0, None)],
        ]

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_relax_internal_data(self, graph_2: Graph):
        router = Router(empty=True)
        router._initialize(graph_2)
        router._relax_internal_data(
            vertex_count=graph_2.get_vertex_count(), vertex_through=2,
        )

        assert router._routes_internal_data == [
            [E(0, None), None, None, None, None],
            [None, E(0, None), E(10, 2), E(25, 3), None],
            [None, None, E(0, None), E(15, 3), None],
            [None, E(20, 4), None, E(0, None), E(17, 5)],
            [None, E(40, 7), E(23, 6), E(38, 3), E(0, None)],
        ]

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_init_router(self, graph_2: Graph):
        router = Router()

        assert router._routes_internal_data == [
            [E(0, None), None, None, None, None],
            [None, E(0, None), E(10, 2), E(25, 3), E(42, 5)],
            [None, E(35, 4), E(0, None), E(15, 3), E(32, 5)],
            [None, E(20, 4), E(30, 2), E(0, None), E(17, 5)],
            [None, E(40, 7), E(23, 6), E(38, 3), E(0, None)],
        ]

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_build_path_no_path(self, graph_2: Graph):
        router = Router()

        for v in range(1, 5):
            assert router.build_path(0, v) is None
            assert router.build_path(v, 0) is None

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_build_path_exist(self, graph_2: Graph):
        router = Router()

        weight, route = router.build_path(vertex_from=2, vertex_to=1)
        assert weight == 35
        assert route == [3, 4]

        weight, route = router.build_path(vertex_from=1, vertex_to=4)
        assert weight == 42
        assert route == [2, 3, 5]

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_path_throh_zero_edge(self):
        graph = Graph()
        for _ in range(3):
            graph.add_vertex()
        graph.add_edge(Edge(from_v=0, to_v=1, weight=2))
        graph.add_edge(Edge(from_v=0, to_v=2, weight=20))
        graph.add_edge(Edge(from_v=1, to_v=2, weight=10))

        router = Router()
        weight, route = router.build_path(vertex_from=0, vertex_to=2)
        assert weight == 12
        assert route == [1, 3]

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_path_to_same_vertex(self, graph_2: Graph):
        router = Router()
        weight, route = router.build_path(vertex_from=1, vertex_to=1)
        assert weight == 0
        assert route == []
