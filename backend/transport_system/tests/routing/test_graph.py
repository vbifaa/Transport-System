import pytest

from routing.models import Edge, Graph


class TestGraph:

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_add_vertex(self):
        graph = Graph()

        for expected_id in range(5):
            id = graph.add_vertex()
            assert expected_id == id
        assert 5 == graph.get_vertex_count()

    @pytest.mark.django_db(transaction=True, reset_sequences=True)
    def test_add_edge(self):
        graph = Graph()
        v0 = graph.add_vertex()
        v1 = graph.add_vertex()

        edge_id01 = Edge(from_v=v0, to_v=v1, weight=23)
        edge_id00 = Edge(from_v=v0, to_v=v0, weight=54)

        edge_id01_id = graph.add_edge(edge_id01)
        edge_id00_id = graph.add_edge(edge_id00)

        assert 2 == graph.get_vertex_count()
        assert [edge_id01_id, edge_id00_id] == list(
            graph.get_incident_edges(v0),
        )
        assert [] == list(graph.get_incident_edges(v1))
        self.assert_edge_and_graph_edge(
            edge=edge_id00,
            graph_edge=graph.get_edge(edge_id00_id.id),
        )
        self.assert_edge_and_graph_edge(
            edge=edge_id01,
            graph_edge=graph.get_edge(edge_id01_id.id),
        )

    def assert_edge_and_graph_edge(self, edge, graph_edge):
        assert edge.from_v == graph_edge.from_v
        assert edge.to_v == graph_edge.to_v
        assert edge.weight == edge.weight
