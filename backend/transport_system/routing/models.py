from dataclasses import dataclass, field
import typing
from unicodedata import name

from django.core.validators import MinValueValidator
from django.db import models

from transport.models import Stop, compute_distance


@dataclass
class Edge:
    from_v: int
    to_v: int
    weight: int
        

@dataclass
class Graph:
    incidence_lists: field(default_factory=typing.List[typing.List[int]])
    edges: field(default_factory=typing.List[Edge])

    def get_vertex_count(self) -> int:
        return len(self.incidence_lists)

    def add_vertex(self) -> int:
        self.incidence_lists.append([])
        return len(self.incidence_lists) - 1

    def add_edge(self, edge: Edge) -> int:
        edge_id = len(self.edges)
        self.edges.append(edge)
        self.incidence_lists[edge.from_v].append(edge_id)
        return edge_id


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
    stop_count = models.PositiveIntegerField(
        'Кол-во остановок, которые надо проехать на автобусе',
        validators=[MinValueValidator(1)]
    )


@dataclass
class RouterWrapper:
    graph: Graph
    bus_time_wait: int = 5

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


    def add_bus(self, bus_name: str, stops: typing.List[str], is_round: bool):
        distances: typing.List[int] = [0]

        stop_count = len(stops)
        for i in range(stop_count - 1):
            dist = compute_distance(from_stop_name=stops[i], to_stop_name=stops[i+1])
            distances.append(distances[-1] + dist)

        for from_stop_id in range(stop_count):
            for to_stop_id in range(from_stop_id + 1, stop_count):
                from_stop = Stop.objects.get(stops[from_stop_id])
                to_stop = Stop.objects.get(stops[to_stop_id])

                edge_id = self.graph.add_edge(
                    Edge(
                        from_v=from_stop.out_id,
                        to_v=to_stop.in_id,
                        weight=distances[to_stop_id] - distances[from_stop_id],
                    )
                )
                RoutePart.objects.create(
                    id=edge_id,
                    type=RoutePart.RoutePartType.BUS,
                    name=bus_name,
                    time=self.bus_time_wait,
                )

