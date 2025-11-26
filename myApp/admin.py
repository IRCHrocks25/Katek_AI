from django.contrib import admin
from .models import OnboardingSession, Client, Tag, SessionTag, InternalNote, Task


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'brand_name', 'email', 'created_at']
    search_fields = ['full_name', 'email', 'brand_name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']


@admin.register(SessionTag)
class SessionTagAdmin(admin.ModelAdmin):
    list_display = ['session', 'tag', 'created_at']


@admin.register(InternalNote)
class InternalNoteAdmin(admin.ModelAdmin):
    list_display = ['session', 'author', 'note_type', 'created_at']
    list_filter = ['note_type', 'created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'session', 'assignee', 'priority', 'completed', 'due_date']
    list_filter = ['priority', 'completed', 'created_at']


@admin.register(OnboardingSession)
class OnboardingSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'course_title', 'status', 'assignee', 'steps_completed', 'created_at']
    list_filter = ['status', 'created_at', 'assignee']
    search_fields = ['session_id', 'course_title', 'client__full_name', 'client__email']
    readonly_fields = ['created_at', 'updated_at', 'submitted_at', 'steps_completed']
    fieldsets = (
        ('Session Info', {
            'fields': ('client', 'user', 'session_id', 'status', 'assignee')
        }),
        ('Quick Access Fields', {
            'fields': ('course_title', 'audience_summary', 'main_outcomes', 'level', 'access_model')
        }),
        ('AI Content', {
            'fields': ('ai_summary', 'ai_outline'),
            'classes': ('collapse',)
        }),
        ('Step Data', {
            'fields': (
                'meet_you', 'course_idea', 'transformation_outcomes',
                'existing_materials', 'brand_vibe', 'course_structure',
                'media_content', 'legal_rights', 'platform_money',
                'timelines_priorities', 'reviews_decision_makers', 'final_uploads'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'submitted_at', 'steps_completed'),
            'classes': ('collapse',)
        }),
    )
