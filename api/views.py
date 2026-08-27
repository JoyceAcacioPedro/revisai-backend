import os
import random
import uuid
import traceback
import requests
from datetime import date

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from django.conf import settings

from .models import User, Subject, Activity, Topic, TopicFile
from .serializers import UserSerializer, SubjectSerializer, ActivitySerializer, TopicSerializer
from .ai_service import generate_revision_plan, generate_summary, generate_flashcards, generate_quiz

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth import get_user_model

from rest_framework import exceptions
User = get_user_model()

# ==========================================
# FUNÇÃO AUXILIAR: ENVIO VIA API HTTP BREVO
# ==========================================
def send_brevo_email(to_email, subject, message):
    api_key = os.getenv('BREVO_API_KEY')
    if not api_key:
        print("❌ ATENÇÃO: BREVO_API_KEY não foi encontrada nas variáveis de ambiente.")
        return False

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    # Remetente verificado na conta Brevo
    payload = {
        "sender": {
            "name": "RevisAI",
            "email": "joyceacaciopedro2005@gmail.com"
        },
        "to": [
            {"email": to_email}
        ],
        "subject": subject,
        "textContent": message
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code in [200, 201, 202]:
            print(f"✅ E-mail enviado via API Brevo com sucesso para {to_email}")
            return True
        else:
            print(f"❌ Erro na API Brevo ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exceção ao ligar à API da Brevo: {str(e)}")
        return False


# ==========================================
# VIEWSETS
# ==========================================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            code = str(random.randint(100000, 999999))
            user.verification_code = code
            user.save()

            subject = 'Welcome to RevisAI — Verify your email'
            message = f'''Hey {user.first_name or "there"}! 👋

Welcome to RevisAI — your AI-powered study companion.

To activate your account, use the verification code below:

━━━━━━━━━━━━━━━━━━
  {code}
━━━━━━━━━━━━━━━━━━

This code expires in 10 minutes.

If you didn't create an account, you can safely ignore this email.

Study smart,
The RevisAI Team ✦'''

            send_brevo_email(user.email, subject, message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Subject.objects.all()

    def get_queryset(self):
        return Subject.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Activity.objects.all()

    def get_queryset(self):
        user = self.request.user
        today = date.today()
        return Activity.objects.filter(user=user, data=today)


class TopicViewSet(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Topic.objects.all()

    def get_queryset(self):
        return Topic.objects.filter(subject__user=self.request.user)

    def perform_create(self, serializer):
        topic = serializer.save(user=self.request.user)

        files = self.request.FILES.getlist('files')
        for f in files:
            TopicFile.objects.create(topic=topic, file=f, name=f.name)

        try:
            from .ai_service import extract_text_from_files
            topic_files = TopicFile.objects.filter(topic=topic)
            files_text = extract_text_from_files(topic_files)

            combined_content = topic.content
            if files_text:
                combined_content += '\n\n' + files_text

            activities = generate_revision_plan(
                topic_title=topic.title,
                topic_content=combined_content if combined_content.strip() else "No content provided",
            )

            for activity in activities:
                Activity.objects.create(
                    user=self.request.user,
                    topic=topic,
                    type=activity["type"],
                    data=activity["date"],
                    status="pending"
                )
        except Exception as e:
            print(f"Erro ao gerar plano de revisão: {e}")


# ==========================================
# ENDPOINTS ADICIONAIS
# ==========================================
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    return Response({
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "username": user.username,
        "date_joined": user.date_joined.strftime('%Y-%m-%d') if user.date_joined else "",
        "country": getattr(user, 'country', ''),
    })


@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def completed_activity(request, pk):
    try:
        activity = Activity.objects.get(pk=pk, user=request.user)
    except Activity.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    activity.status = "Complete"
    activity.save()
    return Response({"message": "Marked as complete"})


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def pending_reviews(request):
    user = request.user
    today = date.today()
    activities = Activity.objects.filter(
        user=user,
        data__gte=today,
        status="pending"
    ).order_by('data')
    serializer = ActivitySerializer(activities, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def progress_topics(request):
    user = request.user
    topics = Topic.objects.filter(subject__user=user)
    progress = {}
    for topic in topics:
        total = Activity.objects.filter(topic=topic).count()
        complete = Activity.objects.filter(topic=topic, status="Complete").count()
        progress[topic.id] = int((complete / total) * 100) if total > 0 else 0
    return Response(progress)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def study_activity(request, pk):
    try:
        activity = Activity.objects.get(pk=pk, user=request.user)
    except Activity.DoesNotExist:
        return Response({"error": "Activity not found"}, status=404)

    today = date.today()
    early = request.query_params.get('early') == 'true'

    if activity.data != today and not early:
        return Response({
            "error": "not_available",
            "message": f"This revision is scheduled for {activity.data}",
            "scheduled_date": str(activity.data)
        }, status=403)

    topic = activity.topic

    try:
        if activity.type == "summary":
            content = generate_summary(topic.title, topic.content)
        elif activity.type == "flashcards":
            content = generate_flashcards(topic.title, topic.content)
        elif activity.type == "quiz":
            content = generate_quiz(topic.title, topic.content)
        else:
            content = {}

        return Response({
            "activity_id": activity.id,
            "type": activity.type,
            "topic_title": topic.title,
            "scheduled_date": str(activity.data),
            "content": content
        })

    except Exception as e:
        print(f"Erro ao gerar conteúdo: {e}")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def send_verification_code(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if user.is_verified:
        return Response({"message": "Already verified"}, status=status.HTTP_200_OK)

    code = str(random.randint(100000, 999999))
    user.verification_code = code
    user.save()

    subject = 'Welcome to RevisAI — Verify your email'
    message = f'''Hey {user.first_name or "there"}! 👋

Welcome to RevisAI — your AI-powered study companion.

To activate your account, use the verification code below:

━━━━━━━━━━━━━━━━━━
  {code}
━━━━━━━━━━━━━━━━━━

This code expires in 10 minutes.

If you didn't create an account, you can safely ignore this email.

Study smart,
The RevisAI Team ✦'''

    send_brevo_email(email, subject, message)
    return Response({"message": "Code sent"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def verify_email(request):
    email = request.data.get('email')
    code = request.data.get('code')

    if not email or not code:
        return Response({"error": "Email e código são obrigatórios"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Converte explicitamente para string e limpa qualquer espaço acidental
    stored_code = str(user.verification_code).strip() if user.verification_code else ""
    received_code = str(code).strip()

    if stored_code and stored_code == received_code:
        user.is_verified = True
        user.verification_code = None
        user.save()
        return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    token = str(uuid.uuid4())
    user.reset_token = token
    user.save()

    reset_link = f"https://revisai-iota.vercel.app/reset-password?token={token}&email={email}"

    message = f'''Hey {user.first_name or "there"}! 👋

We received a request to reset your RevisAI password.

Click the link below to choose a new password:

{reset_link}

This link expires in 1 hour. If you didn't request this, ignore this email — your account is safe.

Study smart,
The RevisAI Team ✦'''

    send_brevo_email(email, 'RevisAI — Reset your password', message)
    return Response({"message": "Reset link sent"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password(request):
    email = request.data.get('email')
    token = request.data.get('token')
    new_password = request.data.get('password')

    try:
        user = User.objects.get(email=email, reset_token=token)
    except User.DoesNotExist:
        return Response({"error": "Invalid token"}, status=400)

    user.set_password(new_password)
    user.reset_token = None
    user.save()

    return Response({"message": "Password reset successfully"})


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # 1. Avisa o Django que o campo 'email' é válido e pode ser recebido
    email = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 2. Desativa a obrigatoriedade do campo padrão 'username'
        self.fields[self.username_field].required = False

    def validate(self, attrs):
        # 3. Agora o código consegue prosseguir e capturar o email em segurança
        email_or_username = attrs.get("email") or attrs.get(self.username_field)
        password = attrs.get("password")

        if not email_or_username or not password:
            raise exceptions.AuthenticationFailed("Email e palavra-passe são obrigatórios.")

        user_obj = User.objects.filter(email__iexact=email_or_username).first() or \
                   User.objects.filter(username__iexact=email_or_username).first()

        if not user_obj:
            raise exceptions.AuthenticationFailed("Utilizador não encontrado.")

        if not user_obj.check_password(password):
            raise exceptions.AuthenticationFailed("Palavra-passe incorreta.")

        if not user_obj.is_active:
            raise exceptions.AuthenticationFailed("Conta inativa.")

        refresh = self.get_token(user_obj)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "email": user_obj.email,
            "username": user_obj.username,
        }

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer