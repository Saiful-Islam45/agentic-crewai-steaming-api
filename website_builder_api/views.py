from django.shortcuts import render

# Create your views here.
# website_builder_api/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from rest_framework import status
import json

from .services.crew_runner import run_market_research_crew

@api_view(['POST'])
def market_research_api(request):
    """
    API endpoint to trigger the CrewAI market research process
    and stream its verbose output.
    """
    location = request.data.get('location')
    niche = request.data.get('niche')


    if not location or not niche:
        return Response(
            {"error": "Both 'location' and 'niche' are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Define a generator function to stream the output
    def event_stream():
        for chunk in run_market_research_crew(location, niche):
            # For SSE, each event should be prefixed with "data: " and end with "\n\n"
            # We'll send each line of verbose output as a separate data chunk.
            yield f"data: {json.dumps({'message': chunk})}\n\n"

    # Use StreamingHttpResponse to stream the generator's output
    # Set content_type to 'text/event-stream' for Server-Sent Events (SSE)
    # This allows the client to process chunks as they arrive.
    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache' # Important for SSE
    return response

