from rest_framework import serializers
from .models import User
from .models import Subject
from .models import Topic, Activity

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'password', 'country', 'date_joined', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'date_joined': {'read_only': True},
            'is_verified': {'read_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            country=validated_data.get('country', ''),
            is_verified=False,
        )
        return user

class SubjectSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Subject
        fields = ['id', 'user', 'subject_name', 'progress']
        
class TopicSerializer(serializers.ModelSerializer):
    # Definimos como read_only para o React não ser obrigado a enviar no FormData
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Topic
        # Incluímos o 'user' explicitamente nos campos aceitos
        fields = ['id', 'user', 'title', 'content', 'subject', 'date']
        read_only_fields = ['date']
    
class TopicNestedSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    
    class Meta:
        model = Topic
        fields = ['id', 'title', 'subject']

class ActivitySerializer(serializers.ModelSerializer):
    topic = TopicNestedSerializer(read_only=True)
    topic_id = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(), source='topic', write_only=True
    )

    class Meta:
        model = Activity
        fields = ['id', 'user', 'topic', 'topic_id', 'type', 'data', 'status']
        read_only_fields = ['user']