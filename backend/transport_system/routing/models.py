import typing
from dataclasses import dataclass, field

from django.core.validators import MinValueValidator
from django.db import models

from transport.models import Bus, Stop, compute_distance


@dataclass
class Edge:
    from_v: int
    to_v: int
    weight: float


class GraphVertex(models.Model):
    count = models.PositiveIntegerField(default=0)


class GraphEdge(models.Model):
    from_v = models.PositiveIntegerField()
    to_v = models.PositiveIntegerField()
    weight = models.FloatField()


class Graph:

    def get_vertex_count(self) -> int:
        if GraphVertex.objects.count() == 0:
            GraphVertex.objects.create(count=0)
        return GraphVertex.objects.all()[0].count

    def get_incident_edges(self, vertex_id: int) -> typing.List[int]:
        return GraphEdge.objects.filter(from_v=vertex_id)

    def get_edge(self, edge_id) -> Edge:
        return GraphEdge.objects.get(id=edge_id)

    def add_vertex(self) -> int:
        if GraphVertex.objects.count() == 0:
            GraphVertex.objects.create(count=0)
        obj = GraphVertex.objects.all()[0]
        obj.count += 1
        obj.save()
        return obj.count - 1

    def add_edge(self, edge: Edge):
        return GraphEdge.objects.create(
            from_v=edge.from_v, to_v=edge.to_v, weight=edge.weight,
        )


@dataclass
class RouteInternalData:
    weight: float
    prev_edge_id: typing.Optional[int]


@dataclass
class Router:

    _routes_internal_data: field(
        default_factory=typing.List[
            typing.List[typing.Optional[RouteInternalData]],
        ],
    )
    graph: Graph

    def __init__(self, empty=False) -> None:
        if empty:
            self._routes_internal_data = []
            return
        graph = Graph()
        self._initialize(graph)

        vertex_count = graph.get_vertex_count()
        for vertex in range(vertex_count):
            self._relax_internal_data(
                vertex_count=vertex_count, vertex_through=vertex,
            )

    def _initialize(self, graph: Graph):
        vertex_count = graph.get_vertex_count()
        self._routes_internal_data = []

        for vertex in range(vertex_count):
            self._routes_internal_data.append([None] * vertex_count)

            for edge in graph.get_incident_edges(vertex):
                route_internal_data = self._routes_internal_data[vertex][
                    edge.to_v
                ]
                if (route_internal_data is None
                   or route_internal_data.weight > edge.weight):
                    self._routes_internal_data[vertex][
                        edge.to_v
                    ] = RouteInternalData(
                        weight=edge.weight, prev_edge_id=edge.id,
                    )
            self._routes_internal_data[vertex][vertex] = RouteInternalData(
                weight=0, prev_edge_id=None,
            )

    def _relax_internal_data(self, vertex_count: int, vertex_through: int):
        for vertex_from in range(vertex_count):
            route_from = self._routes_internal_data[vertex_from][
                vertex_through
            ]
            if route_from:
                for vertex_to in range(vertex_count):
                    route_to = self._routes_internal_data[vertex_through][
                        vertex_to
                    ]
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
            self._routes_internal_data[vertex_from][
                vertex_to
            ] = RouteInternalData(
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
        route_data: RouteInternalData = self._routes_internal_data[
            vertex_from
        ][vertex_to]
        if route_data is None:
            return None

        edge_id = route_data.prev_edge_id
        edges = []
        graph = Graph()
        while edge_id is not None:
            edges.append(edge_id)
            to_v = graph.get_edge(edge_id).from_v
            edge_id = self._routes_internal_data[vertex_from][
                to_v
            ].prev_edge_id
        edges.reverse()
        return route_data.weight, edges


class RoutePart(models.Model):
    id = models.OneToOneField(
        GraphEdge,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    class RoutePartType(models.TextChoices):
        BUS = 'BUS'
        WAIT = 'WAIT'
    type = models.CharField(choices=RoutePartType.choices, max_length=200)
    name = models.CharField(
        '???????????????? ?????????????????? ?????? ???????????????? ?? ?????????????????????? ???? ????????', max_length=26,
    )
    time = models.FloatField(
        '?????????? ?? ????????', validators=[MinValueValidator(0)]
    )
    span_count = models.PositiveIntegerField(
        ('??????-???? ?????????????????????? ?????????? ??????????????????????, '
         '?????????????? ???????? ???????????????? ???? ????????????????'),
        validators=[MinValueValidator(1)],
        default=1,
    )


@dataclass
class RouterWrapper:
    graph: Graph
    router: typing.Optional[Router] = None
    bus_time_wait: float = 5.0

    def add_stop(self, stop_name: str):
        self.router = None

        stop = Stop.objects.get(name=stop_name)
        stop.in_id = self.graph.add_vertex()
        stop.out_id = self.graph.add_vertex()
        stop.save()

        graph_edge_obj = self.graph.add_edge(
            Edge(
                from_v=stop.in_id,
                to_v=stop.out_id,
                weight=self.bus_time_wait,
            ),
        )
        RoutePart.objects.create(
            id=graph_edge_obj,
            type=RoutePart.RoutePartType.WAIT,
            name=stop_name,
            time=self.bus_time_wait,
        )

    def add_bus(
        self, bus_name: str, stops: typing.List[str], one_direction: bool,
    ):
        self.router = None

        bus_velocity = Bus.objects.get(name=bus_name).velocity
        distances: typing.List[int] = [0]

        stop_count = len(stops)
        for i in range(stop_count - 1):
            dist = compute_distance(
                from_stop_name=stops[i], to_stop_name=stops[i + 1],
            )
            dist = dist * 0.06 / bus_velocity
            distances.append(distances[-1] + dist)

        for from_stop_id in range(stop_count):
            for to_stop_id in range(from_stop_id + 1, stop_count):
                from_stop = Stop.objects.get(name=stops[from_stop_id])
                to_stop = Stop.objects.get(name=stops[to_stop_id])

                weight = distances[to_stop_id] - distances[from_stop_id]
                graph_edge_obj = self.graph.add_edge(
                    Edge(
                        from_v=from_stop.out_id,
                        to_v=to_stop.in_id,
                        weight=weight,
                    )
                )
                RoutePart.objects.create(
                    id=graph_edge_obj,
                    type=RoutePart.RoutePartType.BUS,
                    name=bus_name,
                    time=weight,
                    span_count=to_stop_id - from_stop_id,
                )
        if not one_direction:
            stops.reverse()
            self.add_bus(bus_name=bus_name, stops=stops, one_direction=True)

    def build_path(
        self, vertex_from_id, vertex_to_id,
    ) -> typing.Optional[tuple]:
        if self.router is None:
            self.router = Router()
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


router_wrapper = RouterWrapper(Graph())
