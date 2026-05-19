import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from . import models
from .filterfields import EventFilter

class LocationType(DjangoObjectType):
    class Meta:
        model = models.Locations
        fields = "__all__"
        interfaces = (graphene.relay.Node, )

class SharkType(DjangoObjectType):
    class Meta:
        model = models.Shark
        fields = "__all__"
        interfaces = (graphene.relay.Node, )

class EventType(DjangoObjectType):
    class Meta:
        model = models.Event
        fields = "__all__"
        filterset_class = EventFilter
        interfaces = (graphene.relay.Node,)


class ObservationRecordType(DjangoObjectType):
    class Meta:
        model = models.ObservationRecord
        fields = "__all__"
        interfaces = (graphene.relay.Node, )


class ObservationMediaType(DjangoObjectType):
    class Meta:
        model = models.ObservationMedia
        fields = "__all__"
        interfaces = (graphene.relay.Node, )


class EnvironmentalDataType(DjangoObjectType):
    class Meta:
        model = models.EnvironmentalData
        fields = "__all__"
        interfaces = (graphene.relay.Node, )


class SharkBehaviourType(DjangoObjectType):
    class Meta:
        model = models.SharkBehaviour
        fields = "__all__"
        interfaces = (graphene.relay.Node, )

class Query(graphene.ObjectType):
    all_events = DjangoFilterConnectionField(EventType)
    all_sharks = graphene.List(SharkType)
    def resolve_all_sharks(root, info):
        return models.Shark.objects.all()

schema = graphene.Schema(query=Query)