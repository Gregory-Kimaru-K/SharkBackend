import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from . import models
from .filterfields import EventFilter

class EventType(DjangoObjectType):
    class Meta:
        model=models.Event
        fields="__all__"
        filter_fields=EventFilter
    interfaces = (graphene.relay.Node, )

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi!")

schema = graphene.Schema(query=Query)