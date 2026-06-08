from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subject, Topic, Activity

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'country', 'is_verified', 'date_joined', 'is_active']
    list_filter = ['is_active', 'is_verified', 'country', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('Extra', {'fields': ('country', 'is_verified', 'verification_code')}),
    )

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['subject_name', 'user', 'progress']
    list_filter = ['user']
    search_fields = ['subject_name', 'user__email']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'date']
    list_filter = ['subject__user', 'date']
    search_fields = ['title', 'subject__subject_name']
    ordering = ['-date']

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['topic', 'user', 'type', 'data', 'status']
    list_filter = ['status', 'type', 'data']
    search_fields = ['user__email', 'topic__title']
    ordering = ['-data']