from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from openai import OpenAI
from .models import Conversation, Message, Paper
import json
import re
from curl_cffi import requests
from urllib.parse import urlparse

# ============ CONFIGURATION ============

RESEARCH_SYSTEM_PROMPT = """You are a research assistant that helps users find and understand high-quality academic papers.

You must respond with valid JSON in this exact format:
{
    "text": "Your conversational response here. Explain, analyze, or discuss as needed.",
    "papers": [
        {
            "title": "Full paper title",
            "authors": "Author1, Author2, et al.",
            "date": "YYYY",
            "type": "PDF",
            "link": "https://arxiv.org/abs/... or DOI link",
            "summary": "Brief abstract/summary (2-3 sentences)"
        }
    ]
}

Guidelines:
- The "text" field is for your conversational response - use it to explain, provide context, or answer questions
- The "papers" array contains relevant academic papers (include 3-5 when recommending papers)
- Papers array can be empty [] if no papers are relevant to the response
- Only include peer-reviewed, high-quality papers from reputable sources (arXiv, IEEE, ACM, Nature, Science, PubMed, etc.)
- Always include a direct link to the paper (arXiv, DOI, or publisher URL)
- Ensure all paper fields are filled accurately
"""

DEFAULTS = {
    "model": "gpt-5.2",
    "verbosity": "normal",      # minimal | normal | detailed
    "thinking_level": "medium", # low | medium | high
    "web_search": True,
}


# ============ HELPERS ============

def get_openai_client(user):
    """Get OpenAI client with user's API key."""
    api_key = user.profile.openai_api_key
    if not api_key:
        raise ValueError("Please set your OpenAI API key in settings")
    return OpenAI(api_key=api_key)


def build_system_prompt(verbosity, thinking_level, custom_prompt=None, context_papers=None):
    """Build system prompt based on verbosity, thinking level, and context papers."""
    if custom_prompt:
        base = custom_prompt
    else:
        base = RESEARCH_SYSTEM_PROMPT

        # Adjust based on verbosity
        if verbosity == "minimal":
            base += "\n- Keep summaries very brief (1 sentence max)"
        elif verbosity == "detailed":
            base += "\n- Provide detailed summaries (3-4 sentences)"

        # Adjust based on thinking level
        if thinking_level == "high":
            base += "\n- Include seminal/foundational papers in the field"
            base += "\n- Consider interdisciplinary connections"
        elif thinking_level == "low":
            base += "\n- Focus only on the most directly relevant papers"

    # Add context papers if available
    if context_papers and len(context_papers) > 0:
        base += "\n\n## Reference Papers (User's Saved Sources)\n"
        base += "The user has the following papers in their research context. Reference these when relevant:\n\n"
        for i, paper in enumerate(context_papers, 1):
            base += f"{i}. **{paper.title}**\n"
            base += f"   - Authors: {paper.authors}\n"
            base += f"   - Date: {paper.date}\n"
            if paper.link:
                base += f"   - Link: {paper.link}\n"
            base += f"   - Summary: {paper.summary}\n\n"

    return base


def get_context_papers(user):
    """Get user's papers that are marked as in_context."""
    return user.papers.filter(in_context=True)


def call_openai(client, messages, model, web_search):
    """Call OpenAI API with optional web search."""
    if web_search:
        # Use responses API for web search capability
        response = client.responses.create(
            model=model,
            tools=[{"type": "web_search"}],
            input=messages,
        )
        # Extract text from response
        return response.output_text
    else:
        # Use standard chat completions API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content


def parse_papers_response(content):
    """Extract papers JSON from response content."""
    try:
        # Try direct JSON parse first
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Try to find raw JSON object
        match = re.search(r'\{[^{}]*"papers"[^{}]*\[.*?\]\s*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        # Return empty papers array if parsing fails
        return {"papers": [], "error": "Failed to parse response"}


def generate_title(client, model, user_message, assistant_response):
    """Generate a short title for a conversation based on first exchange."""
    prompt = f"""Based on this conversation, generate a short, descriptive title (3-6 words max).
Return ONLY the title text, nothing else.

User: {user_message}

Assistant response summary: {assistant_response[:500] if len(assistant_response) > 500 else assistant_response}"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': 'You generate short, descriptive conversation titles. Return only the title, no quotes or extra text.'},
            {'role': 'user', 'content': prompt}
        ],
        max_completion_tokens=50
    )
    title = response.choices[0].message.content.strip()
    # Remove quotes if present
    title = title.strip('"\'')
    # Limit length
    if len(title) > 100:
        title = title[:100]
    return title


def generate_bibtex(client, model, paper_data):
    """Generate BibTeX citation for a paper."""
    prompt = f"""Generate a proper BibTeX citation for this paper. Return ONLY the BibTeX entry, nothing else.

Title: {paper_data.get('title', '')}
Authors: {paper_data.get('authors', '')}
Year: {paper_data.get('date', '')}
Type: {paper_data.get('type', 'article')}
URL/Link: {paper_data.get('link', '')}

Use @article for journal papers, @inproceedings for conference papers, @misc for preprints/arXiv.
Generate a citation key from the first author's last name and year (e.g., smith2024).
Include all available fields."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': 'You generate accurate BibTeX citations. Return only the BibTeX entry, no explanations.'},
            {'role': 'user', 'content': prompt}
        ],
        max_completion_tokens=500
    )
    bibtex = response.choices[0].message.content.strip()
    # Clean up markdown code blocks if present
    if bibtex.startswith('```'):
        bibtex = re.sub(r'^```(?:bibtex)?\n?', '', bibtex)
        bibtex = re.sub(r'\n?```$', '', bibtex)
    return bibtex


# ============ ENDPOINTS ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """Simple one-off chat - returns papers JSON."""
    message = request.data.get('message', '')
    if not message:
        return Response({'error': 'Message is required'}, status=400)

    # Get config from request or use defaults
    model = request.data.get('model', DEFAULTS['model'])
    verbosity = request.data.get('verbosity', DEFAULTS['verbosity'])
    thinking_level = request.data.get('thinking_level', DEFAULTS['thinking_level'])
    web_search = request.data.get('web_search', DEFAULTS['web_search'])
    custom_prompt = request.data.get('system_prompt')

    try:
        client = get_openai_client(request.user)

        # Get context papers
        context_papers = get_context_papers(request.user)
        system_prompt = build_system_prompt(verbosity, thinking_level, custom_prompt, context_papers)

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': message}
        ]

        content = call_openai(client, messages, model, web_search)
        return Response(parse_papers_response(content))

    except ValueError as e:
        return Response({'error': str(e)}, status=400)
    except Exception as e:
        return Response({'error': f'OpenAI API error: {str(e)}'}, status=500)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def conversation_list(request):
    """List or create conversations."""
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

    # POST - create new conversation
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
    """Get, update, or delete a conversation."""
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

    if request.method == 'PATCH':
        title = request.data.get('title')
        if title:
            conversation.title = title
            conversation.save()
        return Response({
            'id': conversation.id,
            'title': conversation.title,
            'updated_at': conversation.updated_at.isoformat()
        })

    # DELETE
    conversation.delete()
    return Response(status=204)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def conversation_chat(request, pk):
    """Send message in conversation - returns papers JSON."""
    try:
        conversation = request.user.conversations.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation not found'}, status=404)

    message_content = request.data.get('message', '')
    if not message_content:
        return Response({'error': 'Message is required'}, status=400)

    # Get config from request or use defaults
    model = request.data.get('model', DEFAULTS['model'])
    verbosity = request.data.get('verbosity', DEFAULTS['verbosity'])
    thinking_level = request.data.get('thinking_level', DEFAULTS['thinking_level'])
    web_search = request.data.get('web_search', DEFAULTS['web_search'])
    custom_prompt = request.data.get('system_prompt')

    try:
        client = get_openai_client(request.user)

        # Get context papers
        context_papers = get_context_papers(request.user)
        system_prompt = build_system_prompt(verbosity, thinking_level, custom_prompt, context_papers)

        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=message_content,
            system_prompt=system_prompt
        )

        # Build conversation history
        messages = [{'role': 'system', 'content': system_prompt}]
        for msg in conversation.messages.all():
            messages.append({'role': msg.role, 'content': msg.content})

        # Call OpenAI
        content = call_openai(client, messages, model, web_search)
        papers_data = parse_papers_response(content)

        # Save assistant message (store the raw JSON string)
        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=json.dumps(papers_data)
        )

        # Generate title after first exchange (2 messages: 1 user + 1 assistant)
        generated_title = None
        if conversation.messages.count() == 2 and conversation.title == 'New Conversation':
            try:
                assistant_text = papers_data.get('text', str(papers_data))
                generated_title = generate_title(client, model, message_content, assistant_text)
                conversation.title = generated_title
                print(f"[Title Generation] Generated title: {generated_title}")
            except Exception as e:
                print(f"[Title Generation] Error: {e}")
                pass  # Keep default title if generation fails

        # Update conversation timestamp
        conversation.save()

        return Response({
            'user_message': {
                'id': user_message.id,
                'role': 'user',
                'content': message_content,
                'created_at': user_message.created_at.isoformat()
            },
            'assistant_message': {
                'id': assistant_message.id,
                'role': 'assistant',
                'content': papers_data,
                'created_at': assistant_message.created_at.isoformat()
            },
            'conversation_title': conversation.title
        })

    except ValueError as e:
        return Response({'error': str(e)}, status=400)
    except Exception as e:
        return Response({'error': f'OpenAI API error: {str(e)}'}, status=500)


# ============ PAPER ENDPOINTS ============

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def paper_list(request):
    """List or create papers."""
    if request.method == 'GET':
        papers = request.user.papers.all()
        return Response({
            'papers': [
                {
                    'id': p.id,
                    'title': p.title,
                    'authors': p.authors,
                    'date': p.date,
                    'type': p.paper_type,
                    'link': p.link,
                    'summary': p.summary,
                    'bibtex': p.bibtex,
                    'inContext': p.in_context,
                    'created_at': p.created_at.isoformat()
                }
                for p in papers
            ]
        })

    # POST - create new paper
    data = request.data
    paper = Paper.objects.create(
        user=request.user,
        title=data.get('title', ''),
        authors=data.get('authors', ''),
        date=data.get('date', ''),
        paper_type=data.get('type', 'PDF'),
        link=data.get('link', ''),
        summary=data.get('summary', ''),
        in_context=data.get('inContext', True)
    )

    # Return paper immediately without BibTeX - it will be generated via separate endpoint
    return Response({
        'id': paper.id,
        'title': paper.title,
        'authors': paper.authors,
        'date': paper.date,
        'type': paper.paper_type,
        'link': paper.link,
        'summary': paper.summary,
        'bibtex': paper.bibtex,
        'inContext': paper.in_context,
        'created_at': paper.created_at.isoformat()
    }, status=201)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def paper_detail(request, pk):
    """Update or delete a paper."""
    try:
        paper = request.user.papers.get(pk=pk)
    except Paper.DoesNotExist:
        return Response({'error': 'Paper not found'}, status=404)

    if request.method == 'PATCH':
        if 'inContext' in request.data:
            paper.in_context = request.data['inContext']
            paper.save()
        return Response({
            'id': paper.id,
            'title': paper.title,
            'authors': paper.authors,
            'date': paper.date,
            'type': paper.paper_type,
            'link': paper.link,
            'summary': paper.summary,
            'bibtex': paper.bibtex,
            'inContext': paper.in_context
        })

    # DELETE
    paper.delete()
    return Response(status=204)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def paper_generate_bibtex(request, pk):
    """Generate BibTeX citation for a paper."""
    try:
        paper = request.user.papers.get(pk=pk)
    except Paper.DoesNotExist:
        return Response({'error': 'Paper not found'}, status=404)

    try:
        client = get_openai_client(request.user)
        model = DEFAULTS['model']
        bibtex = generate_bibtex(client, model, {
            'title': paper.title,
            'authors': paper.authors,
            'date': paper.date,
            'type': paper.paper_type,
            'link': paper.link
        })
        paper.bibtex = bibtex
        paper.save()
        print(f"[BibTeX Generation] Generated for paper: {paper.title[:30]}")
        return Response({
            'id': paper.id,
            'bibtex': paper.bibtex
        })
    except Exception as e:
        print(f"[BibTeX Generation] Error: {e}")
        return Response({'error': f'Failed to generate BibTeX: {str(e)}'}, status=500)