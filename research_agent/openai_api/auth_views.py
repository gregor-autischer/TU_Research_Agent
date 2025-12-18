from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """Endpoint to get CSRF cookie"""
    return Response({'detail': 'CSRF cookie set'})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new user"""
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=400)

    if len(password) < 8:
        return Response({'error': 'Password must be at least 8 characters'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)

    if email and User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    login(request, user)

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'has_api_key': bool(user.profile.openai_api_key),
            'is_staff': user.is_staff
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login user"""
    username = request.data.get('username', '')
    password = request.data.get('password', '')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'has_api_key': bool(user.profile.openai_api_key),
                'is_staff': user.is_staff
            }
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=401)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout user"""
    logout(request)
    return Response({'detail': 'Logged out successfully'})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user(request):
    """Get current user info"""
    if request.user.is_authenticated:
        return Response({
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'has_api_key': bool(request.user.profile.openai_api_key),
                'is_staff': request.user.is_staff
            }
        })
    return Response({'user': None})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_api_key(request):
    """Save user's OpenAI API key"""
    api_key = request.data.get('api_key', '').strip()

    if not api_key:
        return Response({'error': 'API key is required'}, status=400)

    profile = request.user.profile
    profile.openai_api_key = api_key
    profile.save()

    return Response({'detail': 'API key saved successfully', 'has_api_key': True})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_api_key(request):
    """Delete user's OpenAI API key"""
    profile = request.user.profile
    profile.openai_api_key = None
    profile.save()

    return Response({'detail': 'API key deleted', 'has_api_key': False})
