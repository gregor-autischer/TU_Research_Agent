from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from openai import OpenAI
from .models import Conversation, Message


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


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def conversation_list(request):
    if request.method == 'GET':
        conversations = request.user.conversations.all()
        return Response({
            'conversations': [
                {
                    'id': c.id,
                    'title': c.title,
                    'updated_at': c.updated_at.isoformat(),
                    'preview': c.messages.last().content[:50] if c.messages.exists() else ''
                }
                for c in conversations
            ]
        })
    else:  # POST
        title = request.data.get('title', 'New Conversation')
        conversation = Conversation.objects.create(user=request.user, title=title)
        return Response({
            'id': conversation.id,
            'title': conversation.title,
            'updated_at': conversation.updated_at.isoformat(),
            'messages': []
        }, status=201)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def conversation_detail(request, pk):
    try:
        conversation = request.user.conversations.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation not found'}, status=404)

    if request.method == 'GET':
        return Response({
            'id': conversation.id,
            'title': conversation.title,
            'updated_at': conversation.updated_at.isoformat(),
            'messages': [
                {'id': m.id, 'role': m.role, 'content': m.content, 'created_at': m.created_at.isoformat()}
                for m in conversation.messages.all()
            ]
        })
    elif request.method == 'PATCH':
        title = request.data.get('title')
        if title:
            conversation.title = title
            conversation.save()
        return Response({
            'id': conversation.id,
            'title': conversation.title,
            'updated_at': conversation.updated_at.isoformat()
        })
    else:  # DELETE
        conversation.delete()
        return Response(status=204)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def conversation_chat(request, pk):
    try:
        conversation = request.user.conversations.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation not found'}, status=404)

    message_content = request.data.get('message', '')
    if not message_content:
        return Response({'error': 'Message is required'}, status=400)

    api_key = request.user.profile.openai_api_key
    if not api_key:
        return Response({'error': 'Please set your OpenAI API key in settings'}, status=400)

    # Save user message
    user_message = Message.objects.create(
        conversation=conversation,
        role='user',
        content=message_content
    )

    # Build conversation history for OpenAI
    messages_for_api = [
        {'role': 'system', 'content': 'You are a helpful research assistant that helps users find and understand academic papers.'}
    ]
    for msg in conversation.messages.all():
        messages_for_api.append({'role': msg.role, 'content': msg.content})

    # Call OpenAI with full conversation history
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages_for_api
        )
        assistant_content = response.choices[0].message.content

        # Save assistant message
        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=assistant_content
        )

        # Update conversation timestamp
        conversation.save()

        return Response({
            'user_message': {'id': user_message.id, 'role': 'user', 'content': message_content, 'created_at': user_message.created_at.isoformat()},
            'assistant_message': {'id': assistant_message.id, 'role': 'assistant', 'content': assistant_content, 'created_at': assistant_message.created_at.isoformat()}
        })
    except Exception as e:
        return Response({'error': f'OpenAI API error: {str(e)}'}, status=500)
