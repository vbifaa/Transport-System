from routing.models import Graph, Edge

class TestGraph:
    
    def test_add_vertex(self):
        graph = Graph()

        for expected_id in range(5):
            id = graph.add_vertex()
            assert expected_id == id

    def test_add_edge(self):
        graph = Graph()
        v0 = graph.add_vertex()
        v1 = graph.add_vertex()

        edge_id01 = Edge(from_v=v0, to_v=v1, weight=23)
        edge_id00 = Edge(from_v=v0, to_v=v0, weight=54)
        
        edge_id01_id = graph.add_edge(edge_id01)
        edge_id00_id = graph.add_edge(edge_id00)

        assert 2 == graph.get_vertex_count()
        assert [edge_id01_id, edge_id00_id] == graph.get_incident_edges(v0)
        assert [] == graph.get_incident_edges(v1)
        assert edge_id00 == graph.get_edge(edge_id00_id)
        assert edge_id01 == graph.get_edge(edge_id01_id)
