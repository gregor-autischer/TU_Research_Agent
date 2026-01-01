"""
Verification module for research agent responses.

This module provides a two-step verification process:
1. Paper Verification - Verifies papers using trafilatura and OpenAlex API (only if not already in DB)
2. Comprehensive Response Evaluation - Uses verified paper data to evaluate the assistant's textual response

Paper verifications are stored permanently in the database and reused across verifications.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from openai import OpenAI
from .models import Message, Verification, PaperVerification
import json
import re
import trafilatura
from curl_cffi import requests
from .views import DEFAULTS, get_openai_client
import httpx


# def get_openai_client(user):
#     """Get OpenAI client with user's API key or default."""
#     from django.conf import settings
#     api_key = user.openai_api_key if hasattr(user, 'openai_api_key') and user.openai_api_key else settings.OPENAI_API_KEY
#     return OpenAI(api_key=api_key)


def parse_papers_response(content):
    """Parse JSON response containing text and papers."""
    try:
        data = json.loads(content)
        if 'text' in data and 'papers' in data:
            return data
    except:
        pass
    return None


def fetch_paper_content(url):
    """
    Fetch paper content from URL using trafilatura.
    Returns dict with title, authors, date, and full text.
    Single HTTP request for efficiency.
    """
    if not url:
        return {'error': 'No URL provided', 'success': False}
    
    try:
        # Fetch HTML content with timeout
        response = requests.get(url, impersonate="chrome", timeout=15)
        if response.status_code >= 400:
            return {'error': f'HTTP {response.status_code}', 'success': False}
        
        data = trafilatura.bare_extraction(
            response.text,
            include_comments=False,
            with_metadata=True 
        )
        
        result = {
            'success': True,
            'url': url,
            'title': data.title if data and data.title else None,
            'authors': data.author if data and data.author else None,
            'date': data.date if data and data.date else None,
            'full_text': data.text[:3000] if data and data.text else None,  # First 3000 chars
        }
        
        return result
        
    except Exception as e:
        return {'error': f'Fetch failed: {str(e)[:100]}', 'success': False}


def query_openalex(paper_info):
    """
    Query OpenAlex API for paper metadata using DOI or search by title.
    Returns dict with verified paper information including citations, authors, venue.
    """
    try:
        # Extract DOI from link if present
        doi = None
        link = paper_info.get('link', '')
        if 'doi.org/' in link:
            doi = link.split('doi.org/')[-1]
        
        # Build query
        base_url = "https://api.openalex.org"
        
        if doi:
            # Direct DOI lookup
            url = f"{base_url}/works/doi:{doi}"
                    # Fetch work details
            response = httpx.get(url, timeout=10.0)
            if response.status_code != 200:
                return {'error': f'OpenAlex API error: {response.status_code}', 'success': False}
        
            work = response.json()
        else:
            # Search by title
            title = paper_info.get('title', '')
            if not title:
                return {'error': 'No title or DOI provided', 'success': False}
            
            url = f"{base_url}/works"
            params = {
                'filter': f'title.search:{title}',
                'per-page': 1
            }
            
            response = httpx.get(url, params=params, timeout=10.0)
            if response.status_code != 200:
                return {'error': f'OpenAlex API error: {response.status_code}', 'success': False}
            
            data = response.json()
            results = data.get('results', [])
            if not results:
                return {'error': 'Paper not found in OpenAlex', 'success': False}
            
            # Get detailed work info
            work = results[0]
                
        # Extract relevant metadata (filtered but raw for LLM evaluation)
        primary_location = work.get('primary_location', {})
        source = primary_location.get('source', {}) if primary_location else {}
        
        result = {
            'success': True,
            'title': work.get('title'),
            'doi': work.get('doi'),
            'publication_year': work.get('publication_year'),
            'publication_date': work.get('publication_date'),
            'cited_by_count': work.get('cited_by_count', 0),
            'authors': [
                {
                    'name': author.get('author', {}).get('display_name'),
                    'orcid': author.get('author', {}).get('orcid'),
                    'works_count': author.get('author', {}).get('works_count', 0),
                    'cited_by_count': author.get('author', {}).get('cited_by_count', 0),
                    'h_index': author.get('author', {}).get('summary_stats', {}).get('h_index', 0)
                }
                for author in work.get('authorships', [])
            ],
            'venue': {
                'name': source.get('display_name'),
                'type': source.get('type'),
                'issn': source.get('issn_l'),
            } if source else None,
            'open_access': work.get('open_access', {}).get('is_oa', False),
            'pdf_url': primary_location.get('pdf_url'),
            'referenced_works_count': work.get('referenced_works_count', 0),
            # 'concepts': [
            #     {'name': c.get('display_name'), 'score': c.get('score')}
            #     for c in work.get('concepts', [])[:5]  # Top 5 concepts
            # ]
        }
        
        return result
        
    except httpx.TimeoutException:
        return {'error': 'OpenAlex request timeout', 'success': False}
    except Exception as e:
        return {'error': f'OpenAlex query failed: {str(e)[:100]}', 'success': False}





def verify_single_paper(client, model, paper_info, paper_index):
    """
    Step 1: Verify a single paper using trafilatura and OpenAlex.
    
    Process:
    1. Fetches paper content with trafilatura (single HTTP request) - FIRST
    2. Queries OpenAlex for metadata (citations, authors, venue)
    3. Uses LLM to evaluate the paper comprehensively:
       - Verify content matches claimed paper
       - Evaluate paper quality/credibility based on OpenAlex data
       - Assess assistant's summary accuracy
    
    Returns dict with verification results including LLM-calculated scores.
    """
    
    print(f"[Paper Verification] Verifying paper {paper_index}: {paper_info.get('title', '')[:50]}")
    
    result = {
        'paper_index': paper_index,
        'title': paper_info.get('title', ''),
        'link': paper_info.get('link', ''),
        'claimed_authors': paper_info.get('authors', ''),
        'claimed_date': paper_info.get('date', ''),
        'assistant_summary': paper_info.get('summary', '')
    }
    
    # Step 1.1: Fetch paper content FIRST with trafilatura
    link = paper_info.get('link', '')
    paper_content = fetch_paper_content(link)
    result['content_fetch'] = paper_content
    
    # Step 1.2: Query OpenAlex for metadata
    openalex_data = query_openalex(paper_info)
    result['openalex_metadata'] = openalex_data
    
    # Step 1.3: Use LLM to evaluate everything comprehensively
    verification_prompt = f"""You are evaluating a research paper for verification. Analyze the following information and provide a comprehensive evaluation.

CLAIMED PAPER (from assistant):
Title: {paper_info.get('title', '')}
Authors: {paper_info.get('authors', '')}
Year: {paper_info.get('date', '')}
Link: {paper_info.get('link', '')}
Assistant's Summary: {paper_info.get('summary', 'No summary provided')}

FETCHED CONTENT (from URL):
{json.dumps(paper_content, indent=2)}

OPENALEX METADATA (bibliometric data):
{json.dumps(openalex_data, indent=2)}

Evaluate the paper on these dimensions:

1. **Content Match Verification**:
   - Does the fetched content match the claimed paper information?
   - Title similarity, author match, date match
   - Is this actually an academic/research paper?

2. **Paper Quality & Credibility**:
   - Based on OpenAlex data: citation count, author metrics, venue quality
   - How credible and high-quality is this paper?
   - Consider h-index, citation counts, venue type

3. **Summary Accuracy**:
   - Does the assistant's summary accurately reflect the paper content?
   - Are there any misrepresentations or inaccuracies in the summary?

Respond ONLY with valid JSON in this exact format:
{{
    "content_match": {{
        "matches": <true/false>,
        "confidence": <0-100>,
        "title_match": <true/false>,
        "author_match": <true/false>,
        "date_match": <true/false>,
        "issues": ["<issue 1>", "<issue 2>", ...],
        "explanation": "<brief explanation>"
    }},
    "paper_quality": {{
        "credibility_score": <1-10, based on citations, authors, venue>,
        "quality_score": <1-10, overall academic quality>,
        "credibility_notes": "<explain the credibility assessment>",
        "quality_notes": "<explain the quality assessment>"
    }},
    "summary_evaluation": {{
        "accurate": <true/false>,
        "score": <1-10, how accurate is the summary>,
        "issues": ["<issue 1>", "<issue 2>", ...],
        "notes": "<explanation of summary accuracy>"
    }},
    "overall_assessment": "<2-3 sentence overall evaluation>"
}}

Be thorough and fair. If data is missing (e.g., OpenAlex failed), note it but still evaluate what you have."""
    
    try:
        llm_response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a research paper verification expert. Evaluate papers comprehensively based on fetched content, bibliometric data, and claimed information. Respond only with valid JSON.'
                },
                {'role': 'user', 'content': verification_prompt}
            ],
            temperature=0.1
        )
        
        content = llm_response.choices[0].message.content.strip()
        
        # Parse JSON
        try:
            evaluation = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if match:
                evaluation = json.loads(match.group(1))
            else:
                # Try to find raw JSON object
                match = re.search(r'\{.*"content_match".*\}', content, re.DOTALL)
                if match:
                    evaluation = json.loads(match.group(0))
                else:
                    raise ValueError("Could not parse verification response")
        
        result['content_verification'] = evaluation.get('content_match', {})
        result['paper_quality'] = evaluation.get('paper_quality', {})
        result['summary_evaluation'] = evaluation.get('summary_evaluation', {})
        result['overall_assessment'] = evaluation.get('overall_assessment', '')
        
        # Extract scores for database storage
        result['credibility_score'] = evaluation.get('paper_quality', {}).get('credibility_score', 5.0)
        result['credibility_notes'] = evaluation.get('paper_quality', {}).get('credibility_notes', '')
        result['overall_quality'] = evaluation.get('paper_quality', {}).get('quality_score', 5.0)
        
    except Exception as e:
        print(f"[Paper Verification] LLM evaluation error: {e}")
        # Return fallback structure
        result['content_verification'] = {
            'matches': False,
            'confidence': 0,
            'issues': [f'Evaluation error: {str(e)[:100]}'],
            'explanation': 'LLM evaluation failed'
        }
        result['paper_quality'] = {
            'credibility_score': 5.0,
            'quality_score': 5.0,
            'credibility_notes': 'Evaluation failed',
            'quality_notes': 'Evaluation failed'
        }
        result['summary_evaluation'] = {
            'accurate': False,
            'score': 5.0,
            'issues': ['Evaluation failed'],
            'notes': 'Could not evaluate summary'
        }
        result['overall_assessment'] = f'Paper evaluation failed: {str(e)[:100]}'
        result['credibility_score'] = 5.0
        result['credibility_notes'] = 'Evaluation failed'
        result['overall_quality'] = 5.0
    
    return result


def comprehensive_response_evaluation(client, model, conversation_history, system_prompt, 
                                      assistant_response, papers_data, verified_papers):
    """
    Step 2: Comprehensive evaluation of the assistant's response.
    
    Uses full conversation history, system prompt, original papers data,
    and verified paper information to evaluate the response quality.
    
    This combines textual evaluation with knowledge of verified papers to:
    - Assess response accuracy and relevance
    - Detect hallucinations or misrepresentations
    - Evaluate if paper summaries match verified content
    - Calculate overall confidence score
    
    Returns dict with comprehensive evaluation results.
    """
    
    # Build conversation context
    conversation_context = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation_history
    ])
    
    # Format papers and verifications
    papers_formatted = json.dumps(papers_data, indent=2)
    verified_formatted = json.dumps(verified_papers, indent=2)
    
    evaluation_prompt = f"""You are a scientific verification assistant. Perform a comprehensive evaluation of this research assistant's response.

SYSTEM INSTRUCTIONS (given to the assistant):
{system_prompt}

FULL CONVERSATION HISTORY:
{conversation_context}

ASSISTANT'S RESPONSE TO EVALUATE:
{assistant_response}

PAPERS PROVIDED BY ASSISTANT:
{papers_formatted}

VERIFIED PAPER DATA (from our verification process):
{verified_formatted}

Perform a comprehensive evaluation considering:

1. **Response Quality**:
   - Does it directly address the user's question?
   - Is the explanation clear, helpful, and well-structured?
   - Does it follow the system instructions?

2. **Accuracy & Evidence**:
   - Are claims supported by the verified papers?
   - Do the paper summaries match the verified content?
   - Are there factual errors or misrepresentations?
   - Are papers cited correctly?

3. **Paper Relevance & Quality**:
   - Are the selected papers relevant to the question?
   - Based on verified data, are these high-quality sources?
   - Are low-quality or questionable papers being used?

4. **Hallucination Detection**:
   - Claims made without paper support?
   - Fabricated or exaggerated information?
   - Misrepresentation of paper content?
   - Contradictions with conversation history?

5. **Overall Assessment**:
   - Confidence score (0-100) for the response accuracy
   - Key strengths and concerns
   - Summary of verification findings

Respond ONLY with valid JSON in this exact format:
{{
    "confidence_score": <0-100, overall confidence in response accuracy>,
    "response_quality": {{
        "addresses_question": <true/false>,
        "clear_and_helpful": <true/false>,
        "follows_instructions": <true/false>,
        "score": <1-10>,
        "notes": "<explanation>"
    }},
    "accuracy_assessment": {{
        "claims_supported": <true/false>,
        "summaries_accurate": <true/false>,
        "papers_cited_correctly": <true/false>,
        "factual_errors": ["<error 1>", "<error 2>", ...],
        "score": <1-10>,
        "notes": "<explanation>"
    }},
    "paper_assessment": {{
        "papers_relevant": <true/false>,
        "papers_high_quality": <true/false>,
        "avg_paper_quality": <1-10>,
        "concerns": ["<concern 1>", "<concern 2>", ...],
        "notes": "<explanation>"
    }},
    "hallucination_warnings": [
        {{
            "type": "<unsupported_claim|fabrication|misrepresentation|contradiction>",
            "severity": "<low|medium|high>",
            "description": "<what is potentially hallucinated>",
            "explanation": "<why this is concerning>"
        }}
    ],
    "summary": "<A comprehensive summary (3-5 sentences) of the evaluation results, highlighting key findings, concerns, and validations>"
}}

Be thorough and fair. Acknowledge quality where present, but be specific about concerns."""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a scientific verification assistant. Evaluate research responses comprehensively using verified paper data. Respond only with valid JSON.'
                },
                {'role': 'user', 'content': evaluation_prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON
        try:
            evaluation = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if match:
                evaluation = json.loads(match.group(1))
            else:
                # Try to find raw JSON object
                match = re.search(r'\{.*"confidence_score".*\}', content, re.DOTALL)
                if match:
                    evaluation = json.loads(match.group(0))
                else:
                    raise ValueError("Could not parse evaluation response")
        
        return evaluation
        
    except Exception as e:
        print(f"[Comprehensive Evaluation] Error: {e}")
        import traceback
        traceback.print_exc()
        # Return fallback structure
        return {
            "confidence_score": 50,
            "response_quality": {
                "addresses_question": True,
                "clear_and_helpful": True,
                "follows_instructions": True,
                "score": 5,
                "notes": "Evaluation failed"
            },
            "accuracy_assessment": {
                "claims_supported": True,
                "summaries_accurate": True,
                "papers_cited_correctly": True,
                "factual_errors": [],
                "score": 5,
                "notes": "Evaluation failed"
            },
            "paper_assessment": {
                "papers_relevant": True,
                "papers_high_quality": True,
                "avg_paper_quality": 5,
                "concerns": [],
                "notes": "Evaluation failed"
            },
            "hallucination_warnings": [{
                "type": "error",
                "severity": "high",
                "description": "Comprehensive evaluation failed",
                "explanation": f"Error: {str(e)[:100]}"
            }],
            "summary": f"Evaluation could not be completed: {str(e)[:100]}"
        }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_message(request, message_id):
    """
    Verify an assistant message for accuracy, credibility, and hallucinations.
    
    Two-step verification process:
    1. Paper verification - Validates papers (if not already in DB) using trafilatura + OpenAlex
    2. Comprehensive evaluation - Evaluates response with verified paper knowledge
    
    Returns comprehensive verification results.
    """
    try:
        # Get the message and ensure it belongs to the user's conversation
        message = Message.objects.get(id=message_id)
        if message.conversation.user != request.user:
            return Response({'error': 'Message not found'}, status=404)
        
        if message.role != 'assistant':
            return Response({'error': 'Can only verify assistant messages'}, status=400)
        
        # Check if verification already exists
        existing_verification = message.verifications.first()
        if existing_verification:
            return Response({
                'id': existing_verification.id,
                'message_id': message.id,
                'confidence_score': existing_verification.confidence_score,
                'textual_verification': existing_verification.textual_verification,
                'paper_verifications': existing_verification.get_paper_verifications(),
                'summary': existing_verification.summary,
                'created_at': existing_verification.created_at.isoformat()
            })
        
        # Parse the message content
        parsed_content = parse_papers_response(message.content)
        if not parsed_content:
            return Response({'error': 'Invalid message format'}, status=400)
        
        assistant_text = parsed_content.get('text', '')
        papers = parsed_content.get('papers', [])
        
        # Get the system prompt (from settings or default)
        system_prompt = message.system_prompt
        
        # Get the full conversation history for context
        conversation_history = []
        for msg in message.conversation.messages.filter(created_at__lte=message.created_at).order_by('created_at'):
            content = msg.content
            # For assistant messages, extract text if it's JSON
            if msg.role == 'assistant':
                try:
                    parsed = parse_papers_response(content)
                    if parsed:
                        content = parsed.get('text', content)
                except:
                    pass
            conversation_history.append({
                'role': msg.role,
                'content': content
            })
        
        # Initialize OpenAI client
        client = get_openai_client(request.user)
        # Use model from request or default
        model = request.data.get('model', DEFAULTS['model'])
        
        print(f"[Verification] Starting verification for message {message_id}")
        
        # STEP 1: Verify papers (only if not already in database)
        print(f"[Verification] Step 1: Paper verification ({len(papers)} papers)")
        paper_verifications = []
        
        for i, paper in enumerate(papers):
            # Check if this paper has already been verified (by link)
            link = paper.get('link', '')
            existing_paper_verification = None
            
            if link:
                # Look for existing verification with same link
                existing_paper_verification = PaperVerification.objects.filter(
                    link=link
                ).first()
            
            if existing_paper_verification:
                print(f"[Paper Verification] Using existing verification for: {paper.get('title', '')[:50]}")
                # Reuse existing verification data
                paper_result = {
                    'paper_index': i,
                    'title': existing_paper_verification.title,
                    'link': existing_paper_verification.link,
                    'claimed_authors': existing_paper_verification.claimed_authors,
                    'claimed_date': existing_paper_verification.claimed_date,
                    'assistant_summary': paper.get('summary', ''),
                    'openalex_metadata': existing_paper_verification.openalex_metadata,
                    'verified_metadata': existing_paper_verification.verified_metadata,
                    'content_fetch': existing_paper_verification.content_fetch,
                    'content_verification': existing_paper_verification.content_verification,
                    'paper_quality': existing_paper_verification.paper_quality,
                    'summary_evaluation': existing_paper_verification.summary_evaluation,
                    'overall_assessment': existing_paper_verification.overall_assessment,
                    'credibility_score': existing_paper_verification.credibility_score,
                    'credibility_notes': existing_paper_verification.credibility_notes,
                    'overall_quality': existing_paper_verification.overall_quality,
                    'reused': True  # Flag to indicate this was reused
                }
            else:
                # Perform new verification
                paper_result = verify_single_paper(
                    client=client,
                    model=model,
                    paper_info=paper,
                    paper_index=i
                )
                paper_result['reused'] = False
            
            paper_verifications.append(paper_result)
        
        # STEP 2: Comprehensive response evaluation with verified paper knowledge
        print(f"[Verification] Step 2: Comprehensive response evaluation")
        comprehensive_eval = comprehensive_response_evaluation(
            client=client,
            model=model,
            conversation_history=conversation_history,
            system_prompt=system_prompt,
            assistant_response=assistant_text,
            papers_data=papers,
            verified_papers=paper_verifications
        )
        
        # Use confidence score from comprehensive evaluation
        final_confidence_score = comprehensive_eval.get('confidence_score', 50)
        final_summary = comprehensive_eval.get('summary', '')
        
        # Save verification to database
        verification = Verification.objects.create(
            message=message,
            confidence_score=round(final_confidence_score, 1),
            textual_verification=comprehensive_eval,
            summary=final_summary
        )
        
        # Save paper verifications as separate model instances (only new ones)
        for paper_result in paper_verifications:
            # Check if this was reused - don't create duplicate
            if paper_result.get('reused', False):
                # Link existing paper verification to this verification
                # Find the existing one and update if needed, or just skip
                # For now, we'll create a new entry for this verification
                # (allows same paper to be part of multiple verifications)
                pass
            
            # Always create new PaperVerification for this Verification
            PaperVerification.objects.create(
                verification=verification,
                paper_index=paper_result.get('paper_index', 0),
                title=paper_result.get('title', ''),
                link=paper_result.get('link', ''),
                claimed_authors=paper_result.get('claimed_authors', ''),
                claimed_date=paper_result.get('claimed_date', ''),
                openalex_metadata=paper_result.get('openalex_metadata'),
                verified_metadata=paper_result.get('verified_metadata'),
                content_fetch=paper_result.get('content_fetch'),
                content_verification=paper_result.get('content_verification'),
                paper_quality=paper_result.get('paper_quality'),
                summary_evaluation=paper_result.get('summary_evaluation'),
                overall_assessment=paper_result.get('overall_assessment', ''),
                credibility_score=paper_result.get('credibility_score', 5.0),
                credibility_notes=paper_result.get('credibility_notes', ''),
                overall_quality=paper_result.get('overall_quality', 5.0)
            )
        
        print(f"[Verification] Completed. Confidence: {final_confidence_score:.1f}")
        
        return Response({
            'id': verification.id,
            'message_id': message.id,
            'confidence_score': verification.confidence_score,
            'textual_verification': verification.textual_verification,
            'paper_verifications': verification.get_paper_verifications(),
            'summary': verification.summary,
            'created_at': verification.created_at.isoformat()
        }, status=201)
    
    except Message.DoesNotExist:
        return Response({'error': 'Message not found'}, status=404)
    except ValueError as e:
        return Response({'error': str(e)}, status=400)
    except Exception as e:
        print(f"[Verification] Error: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': f'Verification failed: {str(e)}'}, status=500)
