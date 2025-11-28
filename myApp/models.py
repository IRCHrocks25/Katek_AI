from django.db import models
from django.contrib.auth.models import User
import json


class Client(models.Model):
    """Client/Creator information"""
    full_name = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.full_name or self.email


class OnboardingSession(models.Model):
    """Stores onboarding wizard data for course creation"""
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_review', 'In Review'),
        ('needs_clarification', 'Needs Clarification'),
        ('approved', 'Approved Blueprint'),
        ('in_production', 'In Production'),
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),  # Legacy
        ('submitted', 'Submitted'),  # Legacy
    ]
    
    # Client reference
    client = models.ForeignKey(
        'Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions'
    )
    
    # User reference (can be null for anonymous sessions)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='onboarding_sessions'
    )
    
    # Session identifier for anonymous users
    session_id = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Assignee (team member)
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_sessions',
        verbose_name='Assigned To'
    )
    
    # Denormalized important fields for quick access
    course_title = models.CharField(max_length=500, blank=True)
    audience_summary = models.TextField(blank=True)
    main_outcomes = models.TextField(blank=True)
    level = models.CharField(max_length=50, blank=True)  # Beginner, Intermediate, Advanced
    access_model = models.CharField(max_length=50, blank=True)  # Free, One-time, Subscription
    
    # AI-generated content
    ai_summary = models.TextField(blank=True)
    ai_outline = models.JSONField(default=dict, blank=True)
    
    # Progress tracking
    steps_completed = models.IntegerField(default=0)
    
    # Step data stored as JSON
    # Step 1: Meet You
    meet_you = models.JSONField(default=dict, blank=True)
    
    # Step 2: Your Course Idea
    course_idea = models.JSONField(default=dict, blank=True)
    
    # Step 3: Transformation & Outcomes
    transformation_outcomes = models.JSONField(default=dict, blank=True)
    
    # Step 4: What You Already Have
    existing_materials = models.JSONField(default=dict, blank=True)
    
    # Step 5: Brand & Vibe
    brand_vibe = models.JSONField(default=dict, blank=True)
    
    # Step 6: Course Structure & Interactivity
    course_structure = models.JSONField(default=dict, blank=True)
    
    # Step 7: Your Face & Voice (Media)
    media_content = models.JSONField(default=dict, blank=True)
    
    # Step 8: Legal & Rights
    legal_rights = models.JSONField(default=dict, blank=True)
    
    # Step 9: Platform & Money
    platform_money = models.JSONField(default=dict, blank=True)
    
    # Step 10: Timelines & Priorities
    timelines_priorities = models.JSONField(default=dict, blank=True)
    
    # Step 11: Reviews & Decision-Makers
    reviews_decision_makers = models.JSONField(default=dict, blank=True)
    
    # Step 12: Final Uploads & Secret Notes
    final_uploads = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['session_id', 'status']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else f"Session {self.session_id}"
        return f"Onboarding: {user_str} - {self.status}"
    
    def get_all_data(self):
        """Returns all step data as a single dictionary"""
        return {
            'meet_you': self.meet_you,
            'course_idea': self.course_idea,
            'transformation_outcomes': self.transformation_outcomes,
            'existing_materials': self.existing_materials,
            'brand_vibe': self.brand_vibe,
            'course_structure': self.course_structure,
            'media_content': self.media_content,
            'legal_rights': self.legal_rights,
            'platform_money': self.platform_money,
            'timelines_priorities': self.timelines_priorities,
            'reviews_decision_makers': self.reviews_decision_makers,
            'final_uploads': self.final_uploads,
        }
    
    def update_step_data(self, step_name, data):
        """Updates data for a specific step"""
        if hasattr(self, step_name):
            current_data = getattr(self, step_name) or {}
            if isinstance(current_data, dict) and isinstance(data, dict):
                current_data.update(data)
                setattr(self, step_name, current_data)
            else:
                setattr(self, step_name, data)
            self.save(update_fields=[step_name, 'updated_at'])
    
    def calculate_progress(self, save=True):
        """Calculate how many steps have been completed"""
        steps = [
            self.meet_you, self.course_idea, self.transformation_outcomes,
            self.existing_materials, self.brand_vibe, self.course_structure,
            self.media_content, self.legal_rights, self.platform_money,
            self.timelines_priorities, self.reviews_decision_makers, self.final_uploads
        ]
        completed = sum(1 for step in steps if step and isinstance(step, dict) and len(step) > 0)
        self.steps_completed = completed
        if save:
            self.save(update_fields=['steps_completed'])
        return completed
    
    def extract_denormalized_fields(self):
        """Extract important fields from JSON data for quick access"""
        # Course title
        if self.course_idea and isinstance(self.course_idea, dict):
            self.course_title = self.course_idea.get('course_title', '') or self.course_title
        
        # Audience
        if self.course_idea and isinstance(self.course_idea, dict):
            self.audience_summary = self.course_idea.get('target_audience', '') or self.audience_summary
        
        # Outcomes
        if self.transformation_outcomes and isinstance(self.transformation_outcomes, dict):
            outcomes = self.transformation_outcomes.get('learning_outcomes', '')
            if isinstance(outcomes, str):
                self.main_outcomes = outcomes
            elif isinstance(outcomes, list):
                self.main_outcomes = '\n'.join(outcomes)
        
        # Access model
        if self.platform_money and isinstance(self.platform_money, dict):
            self.access_model = self.platform_money.get('pricing_model', '') or self.access_model


class Tag(models.Model):
    """Tags for categorizing sessions"""
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#3b82f6')  # Hex color
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class SessionTag(models.Model):
    """Many-to-many relationship between sessions and tags"""
    session = models.ForeignKey(OnboardingSession, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['session', 'tag']


class InternalNote(models.Model):
    """Internal notes and comments on sessions"""
    NOTE_TYPES = [
        ('general', 'General'),
        ('content', 'Content'),
        ('legal', 'Legal'),
        ('platform', 'Platform'),
        ('clarification', 'Clarification Needed'),
    ]
    
    session = models.ForeignKey(OnboardingSession, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note by {self.author} on {self.session}"


class Task(models.Model):
    """Tasks linked to sessions"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    session = models.ForeignKey(OnboardingSession, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'due_date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.session}"


# ==================== WEBSITE CONTENT MODELS ====================

class MediaAsset(models.Model):
    """Cloudinary image assets for website content"""
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    cloudinary_url = models.URLField(max_length=500)
    cloudinary_public_id = models.CharField(max_length=255, blank=True)
    original_url = models.URLField(max_length=500, blank=True)
    web_url = models.URLField(max_length=500, blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    folder = models.CharField(max_length=255, default='katek_ai/uploads')
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    format = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title or self.cloudinary_public_id or 'Untitled Asset'


class SEO(models.Model):
    """SEO metadata for homepage"""
    page_title = models.CharField(max_length=200, default='KaTek AI - All-in-One AI CRM & Growth Engine')
    meta_description = models.TextField(max_length=500, default='Transform your business with KaTek AI - the complete CRM and growth platform.')
    meta_keywords = models.CharField(max_length=500, blank=True)
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.TextField(max_length=500, blank=True)
    og_image_url = models.URLField(max_length=500, blank=True)
    twitter_card = models.CharField(max_length=50, default='summary_large_image', blank=True)
    canonical_url = models.URLField(max_length=500, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "SEO"
        verbose_name_plural = "SEO"
    
    def __str__(self):
        return f"SEO - {self.page_title}"


class WebsiteHero(models.Model):
    """Hero section content"""
    pill_label = models.CharField(max_length=100, default='ALL-IN-ONE AI CRM')
    main_headline = models.CharField(max_length=500, default='Stop juggling 17 tools. One system that connects everything.')
    subheadline = models.TextField(blank=True)
    primary_cta_text = models.CharField(max_length=100, default='Schedule Your Call')
    primary_cta_link = models.URLField(max_length=500, blank=True)
    secondary_cta_text = models.CharField(max_length=100, blank=True)
    secondary_cta_link = models.URLField(max_length=500, blank=True)
    background_image_url = models.URLField(max_length=500, blank=True)
    dashboard_image_url = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Section"
    
    def __str__(self):
        return f"Hero - {self.main_headline[:50]}"


class WebsiteSection(models.Model):
    """Generic website section content"""
    SECTION_TYPES = [
        ('story', 'Story Section'),
        ('platform', 'Platform Section'),
        ('outcomes', 'Outcomes Section'),
        ('ai_sales', 'AI Sales Section'),
        ('campaign_manager', 'Campaign Manager Section'),
        ('geo_distribution', 'GEO Distribution Section'),
        ('reputation', 'Reputation Section'),
        ('ai_websites', 'AI Websites Section'),
        ('personas', 'Personas Section'),
        ('testimonials', 'Testimonials Section'),
        ('final_cta', 'Final CTA Section'),
    ]
    
    section_type = models.CharField(max_length=50, choices=SECTION_TYPES, unique=True)
    title = models.CharField(max_length=500, blank=True)
    subtitle = models.TextField(blank=True)
    description = models.TextField(blank=True)
    content = models.JSONField(default=dict, blank=True)  # Flexible JSON for section-specific content
    background_image_url = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'section_type']
        verbose_name = "Website Section"
        verbose_name_plural = "Website Sections"
    
    def __str__(self):
        return f"{self.get_section_type_display()} - {self.title or 'Untitled'}"


class WebsiteTestimonial(models.Model):
    """Testimonials for website"""
    quote = models.TextField()
    author_name = models.CharField(max_length=200)
    author_title = models.CharField(max_length=200, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return f"{self.author_name} - {self.quote[:50]}"


class WebsiteFooter(models.Model):
    """Footer content"""
    copyright_text = models.CharField(max_length=500, default='© 2024 KaTek AI. All rights reserved.')
    social_links = models.JSONField(default=dict, blank=True)  # {platform: url}
    footer_links = models.JSONField(default=list, blank=True)  # [{title, url}]
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Footer"
        verbose_name_plural = "Footer"
    
    def __str__(self):
        return "Website Footer"