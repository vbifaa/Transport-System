from dataclasses import dataclass, field
import typing

from django.core.validators import MinValueValidator
from django.db import models

from transport.models import Bus, Stop, compute_distance


@dataclass
class Edge:
    from_v: int
    to_v: int
    weight: int
        

@dataclass
class Graph:
    _incidence_lists: field(default_factory=typing.List[typing.List[int]])
    _edges: field(default_factory=typing.List[Edge])

    def __init__(self) -> None:
        self._incidence_lists = []
        self._edges = []

    def get_vertex_count(self) -> int:
        return len(self._incidence_lists)

    def get_incident_edges(self, vertex_id: int) -> typing.List[int]:
        return self._incidence_lists[vertex_id]

    def get_edge(self, edge_id) -> Edge:
        return self._edges[edge_id]

    def add_vertex(self) -> int:
        self._incidence_lists.append([])
        return len(self._incidence_lists) - 1

    def add_edge(self, edge: Edge) -> int:
        edge_id = len(self._edges)
        self._edges.append(edge)
        self._incidence_lists[edge.from_v].append(edge_id)
        return edge_id


@dataclass
class RouteInternalData:
    weight: float
    prev_edge_id: typing.Optional[int]


@dataclass
class Router:

    _routes_internal_data: field(
        default_factory=typing.List[typing.List[typing.Optional[RouteInternalData]]],
    )
    graph: Graph

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self._initialize(graph)

        vertex_count = graph.get_vertex_count()
        for vertex in range(vertex_count):
            self._relax_internal_data(vertex_count=vertex_count, vertex_through=vertex)
    
    def _initialize(self, graph: Graph):
        vertex_count = graph.get_vertex_count()
        self._routes_internal_data = []

        for vertex in range(vertex_count):
            self._routes_internal_data.append([None] * vertex_count)

            for edge_id in graph.get_incident_edges(vertex):
                edge = graph.get_edge(edge_id)
                route_internal_data = self._routes_internal_data[vertex][edge.to_v]
                if route_internal_data is None or route_internal_data.weight > edge.weight:
                    self._routes_internal_data[vertex][edge.to_v] = RouteInternalData(weight=edge.weight, prev_edge_id=edge_id)
            self._routes_internal_data[vertex][vertex] = RouteInternalData(weight=0, prev_edge_id=None)

    def _relax_internal_data(self, vertex_count: int, vertex_through: int):
        for vertex_from in range(vertex_count):
            route_from = self._routes_internal_data[vertex_from][vertex_through]
            if route_from:
                for vertex_to in range(vertex_count):
                    route_to = self._routes_internal_data[vertex_through][vertex_to]
                    if route_to:
                        self._relax_route(
                            vertex_from=vertex_from,
                            vertex_to=vertex_to,
                            route_from=route_from,
                            route_to=route_to,
                        )

    def _relax_route(
        self,
        vertex_from: int,
        vertex_to: int,
        route_from: RouteInternalData,
        route_to: RouteInternalData,
    ):
        route_relaxing = self._routes_internal_data[vertex_from][vertex_to]
        candidate_weight = route_from.weight + route_to.weight
        if route_relaxing is None or candidate_weight < route_relaxing.weight:
            self._routes_internal_data[vertex_from][vertex_to] = RouteInternalData(
                weight=candidate_weight,
                prev_edge_id=(
                    route_to.prev_edge_id 
                    if route_to.prev_edge_id
                    else route_from.prev_edge_id
                ),
            )

    def build_path(
        self, vertex_from: int, vertex_to: int,
    ) -> typing.Optional[typing.Tuple[float, typing.List[int]]]:
        route_data: RouteInternalData = self._routes_internal_data[vertex_from][vertex_to]
        if route_data is None:
            return None

        edge_id = route_data.prev_edge_id
        edges = []
        while edge_id is not None:
            edges.append(edge_id)
            to_v = self.graph.get_edge(edge_id).from_v
            edge_id = self._routes_internal_data[vertex_from][to_v].prev_edge_id
        edges.reverse()
        return route_data.weight, edges


class RoutePart(models.Model):

    class RoutePartType(models.TextChoices):
        BUS = 'BUS'
        WAIT = 'WAIT'
    type = models.CharField(choices=RoutePartType.choices, max_length=200)
    name = models.CharField(
        'Название остановки или автобуса в зависимости от типа', max_length=26,
    )
    time = models.FloatField(
        'Время в пути', validators=[MinValueValidator(0)]
    )
    span_count = models.PositiveIntegerField(
        'Кол-во промежутков между остановками, которые надо проехать на автобусе',
        validators=[MinValueValidator(1)],
        default=1,
    )


@dataclass
class RouterWrapper:
    graph: Graph
    router: typing.Optional[Router] = None
    bus_time_wait: float = 5.0

    def add_stop(self, stop_name: str):
        stop = Stop.objects.get(name=stop_name)
        stop.in_id = self.graph.add_vertex()
        stop.out_id = self.graph.add_vertex()
        stop.save()

        edge_id = self.graph.add_edge(
            Edge(from_v=stop.in_id, to_v=stop.out_id, weight=self.bus_time_wait),
        )
        RoutePart.objects.create(
            id=edge_id,
            type=RoutePart.RoutePartType.WAIT,
            name=stop_name,
            time=self.bus_time_wait,
        )


    def add_bus(self, bus_name: str, stops: typing.List[str], one_direction: bool):
        bus_velocity = Bus.objects.get(name=bus_name).velocity
        distances: typing.List[int] = [0]

        stop_count = len(stops)
        for i in range(stop_count - 1):
            dist = compute_distance(from_stop_name=stops[i], to_stop_name=stops[i+1])
            dist = dist * 0.06 / bus_velocity
            distances.append(distances[-1] + dist)

        for from_stop_id in range(stop_count):
            for to_stop_id in range(from_stop_id + 1, stop_count):
                from_stop = Stop.objects.get(name=stops[from_stop_id])
                to_stop = Stop.objects.get(name=stops[to_stop_id])

                weight = distances[to_stop_id] - distances[from_stop_id]
                edge_id = self.graph.add_edge(
                    Edge(
                        from_v=from_stop.out_id,
                        to_v=to_stop.in_id,
                        weight=weight,
                    )
                )
                RoutePart.objects.create(
                    id=edge_id,
                    type=RoutePart.RoutePartType.BUS,
                    name=bus_name,
                    time=weight,
                    span_count=to_stop_id - from_stop_id,
                )
        if not one_direction:
            stops.reverse()
            self.add_bus(bus_name=bus_name, stops=stops, one_direction=True)

    def build_path(self, vertex_from_id, vertex_to_id) -> typing.Optional[tuple]:
        if self.router is None:
            self.router = Router(self.graph)
        res = self.router.build_path(
            vertex_from=vertex_from_id, vertex_to=vertex_to_id,
        )
        if res is None:
            return None
        weight, route = res
        return (
            weight,
            [RoutePart.objects.get(id=id) for id in route],
        )
