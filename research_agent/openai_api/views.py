from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from openai import OpenAI


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    message = request.data.get('message', '')

    if not message:
        return Response({'error': 'Message is required'}, status=400)

    # Get API key from user's profile (mandatory)
    api_key = request.user.profile.openai_api_key
    if not api_key:
        return Response({'error': 'Please set your OpenAI API key in settings'}, status=400)

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': 'You are a helpful research assistant that helps users find and understand academic papers.'},
                {'role': 'user', 'content': message}
            ]
        )
        return Response({'response': response.choices[0].message.content})
    except Exception as e:
        return Response({'error': f'OpenAI API error: {str(e)}'}, status=500)
