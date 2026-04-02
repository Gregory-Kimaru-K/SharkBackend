from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from . import serializers
from .models import Shark

@api_view(['POST'])
def shark_view(request):
    serializer = serializers.SharkSerializer(data=request.data)
    if serializer.is_valid():
        shark = serializer.save()
        # Return the full created object so the client can render it immediately.
        # (The create endpoint is the "get it from" route.)
        return Response(
            {
                "message": "Shark created successfully",
                "shark": serializers.SharkSerializer(shark).data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def sharks_list_view(request):
    sharks = Shark.objects.all().order_by('name')
    serializer = serializers.SharkSerializer(sharks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def location_view(request):
    serializer = serializers.LocationSerializer(data=request.data)
    if serializer.is_valid():
        location = serializer.save()
        return Response(
            {
                "message": "Location created successfully",
                "location": serializers.LocationSerializer(location).data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def event_view(request):
    serializer = serializers.EventSerializer(data=request.data)

    if serializer.is_valid():

        event = serializer.save()

        return Response(
            {
                "message": "Event + environmental data created successfully",
                "event": serializers.EventSerializer(event).data
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def observation_view(request):
    # force source_type to USER
    data = request.data.copy()
    data['source_type'] = 'USER'

    serializer = serializers.ObservationRecordSerializer(data=data)
    if serializer.is_valid():
        observation = serializer.save()
        return Response(
            {
                "message": "Observation recorded successfully",
                "observation": serializers.ObservationRecordSerializer(observation).data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def observation_media_view(request):
    serializer = serializers.ObservationMediaSerializer(data=request.data)
    if serializer.is_valid():
        media = serializer.save()
        return Response({
            "message": "Media uploaded successfully",
            "media_id": media.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def shark_behaviour(request):
    data = request.data.copy()

    # force event from request GET param, URL, or some logic
    # e.g., ?event_id=269209d2-3312-40ee-9c29-1992c9841bde
    event_id = request.GET.get('event_id') or request.data.get('event')
    if not event_id:
        return Response({"error": "Event ID is required"}, status=400)
    
    data['event'] = event_id

    serializer = serializers.SharkBehaviourSerializer(data=data)
    if serializer.is_valid():
        behaviour = serializer.save()
        return Response(
            {
                "message": "Shark behaviour saved",
                "behaviour": serializers.SharkBehaviourSerializer(behaviour).data,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=400)
