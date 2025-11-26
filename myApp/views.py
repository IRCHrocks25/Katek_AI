from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.db.models import Count, Q, F
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json
import uuid
import csv
from .models import OnboardingSession, Client, Tag, SessionTag, InternalNote, Task
import openai


def home(request):
    return render(request, 'myApp/home.html')


def onboarding(request):
    """Main onboarding wizard page"""
    return render(request, 'myApp/onboarding.html')


def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('dashboard_overview')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    
    return render(request, 'myApp/login.html')


def logout_view(request):
    """Custom logout view"""
    logout(request)
    return redirect('login')


@csrf_exempt
@require_http_methods(["POST"])
def onboarding_save(request):
    """API endpoint to save/autosave onboarding data"""
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid JSON: {str(e)}'
            }, status=400)
        
        # Get or create session
        session_id = data.get('session_id')
        user = request.user if request.user.is_authenticated else None
        
        if session_id:
            session = OnboardingSession.objects.filter(session_id=session_id).first()
            if not session:
                session = OnboardingSession.objects.create(
                    session_id=session_id,
                    user=user
                )
        elif user:
            # Get most recent in-progress session for this user
            session = OnboardingSession.objects.filter(
                user=user,
                status='in_progress'
            ).order_by('-created_at').first()
            
            if not session:
                session = OnboardingSession.objects.create(
                    user=user,
                    session_id=str(uuid.uuid4())
                )
        else:
            # Create new anonymous session
            session = OnboardingSession.objects.create(
                session_id=str(uuid.uuid4())
            )
        
        # Update step data
        step_mapping = {
            'meet_you': 'meet_you',
            'course_idea': 'course_idea',
            'transformation_outcomes': 'transformation_outcomes',
            'existing_materials': 'existing_materials',
            'brand_vibe': 'brand_vibe',
            'course_structure': 'course_structure',
            'media_content': 'media_content',
            'legal_rights': 'legal_rights',
            'platform_money': 'platform_money',
            'timelines_priorities': 'timelines_priorities',
            'reviews_decision_makers': 'reviews_decision_makers',
            'final_uploads': 'final_uploads',
        }
        
        # Process each step individually - save even if some steps have errors
        steps_data = data.get('steps', {})
        if not steps_data:
            # If no steps data, just return success (might be a ping or empty save)
            return JsonResponse({
                'success': True,
                'session_id': session.session_id,
                'message': 'Session updated'
            })
        
        saved_steps = []
        errors = []
        
        for step_key, step_data in steps_data.items():
            try:
                if step_key in step_mapping:
                    field_name = step_mapping[step_key]
                    
                    # Ensure step_data is a dictionary
                    if not isinstance(step_data, dict):
                        step_data = {}
                    
                    # Get current data or initialize as empty dict
                    current_data = getattr(session, field_name)
                    if not isinstance(current_data, dict):
                        current_data = {}
                    
                    # Update with new data
                    current_data.update(step_data)
                    setattr(session, field_name, current_data)
                    saved_steps.append(step_key)
                    
                    # If this is meet_you step, create/link Client
                    if step_key == 'meet_you' and step_data:
                        email = step_data.get('email', '').strip()
                        full_name = step_data.get('full_name', '').strip()
                        if email and full_name:
                            client, created = Client.objects.get_or_create(
                                email=email,
                                defaults={
                                    'full_name': full_name,
                                    'brand_name': step_data.get('brand_name', ''),
                                    'phone': step_data.get('phone', ''),
                                    'website': step_data.get('website', ''),
                                }
                            )
                            if not created:
                                # Update existing client
                                client.full_name = full_name
                                if step_data.get('brand_name'):
                                    client.brand_name = step_data.get('brand_name', '')
                                if step_data.get('phone'):
                                    client.phone = step_data.get('phone', '')
                                if step_data.get('website'):
                                    client.website = step_data.get('website', '')
                                client.save()
                            session.client = client
                            session.save(update_fields=['client'])
                    
                    # Extract denormalized fields for quick access
                    if step_key == 'course_idea' and step_data:
                        session.course_title = step_data.get('course_title', '') or session.course_title
                        session.audience_summary = step_data.get('target_audience', '') or session.audience_summary
                    elif step_key == 'transformation_outcomes' and step_data:
                        outcomes = step_data.get('learning_outcomes', '')
                        if isinstance(outcomes, str):
                            session.main_outcomes = outcomes or session.main_outcomes
                        elif isinstance(outcomes, list):
                            session.main_outcomes = '\n'.join(outcomes) or session.main_outcomes
                    elif step_key == 'platform_money' and step_data:
                        session.access_model = step_data.get('pricing_model', '') or session.access_model
                    
                else:
                    errors.append(f'Unknown step: {step_key}')
            except Exception as step_error:
                errors.append(f'Error saving {step_key}: {str(step_error)}')
                # Continue with other steps even if one fails
        
        # Calculate progress after all steps are processed
        session.calculate_progress(save=False)  # Don't save yet, we'll save everything together
        
        # Check if this is a final submission
        if data.get('submit', False):
            session.status = 'submitted'
            if hasattr(session, 'submitted_at'):
                from django.utils import timezone
                session.submitted_at = timezone.now()
        
        # Save the session with all updates including progress
        try:
            # Build list of fields to update
            update_fields = ['steps_completed', 'updated_at']
            
            # Add denormalized fields if they were updated
            if any(step_key in ['course_idea', 'transformation_outcomes', 'platform_money'] for step_key in saved_steps):
                update_fields.extend(['course_title', 'audience_summary', 'main_outcomes', 'access_model'])
            
            if data.get('submit', False):
                update_fields.extend(['status', 'submitted_at'])
            
            session.save(update_fields=update_fields)
        except Exception as save_error:
            return JsonResponse({
                'success': False,
                'error': f'Failed to save session: {str(save_error)}',
                'saved_steps': saved_steps,
                'errors': errors
            }, status=400)
        
        # Return success even if some steps had errors (partial save)
        response_data = {
            'success': True,
            'session_id': session.session_id,
            'message': 'Data saved successfully',
            'saved_steps': saved_steps
        }
        
        if errors:
            response_data['warnings'] = errors
        
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_message = str(e)
        
        # Check if it's a database table missing error
        if 'does not exist' in error_message or 'relation' in error_message.lower():
            error_message = 'Database table not found. Please run migrations: python manage.py makemigrations && python manage.py migrate'
        
        print(f"Save error: {error_trace}")  # Log to console for debugging
        
        return JsonResponse({
            'success': False,
            'error': error_message,
            'details': error_trace if settings.DEBUG else None
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def onboarding_ai_help(request):
    """API endpoint for AI assistance on specific fields"""
    try:
        data = json.loads(request.body)
        field_type = data.get('field_type')  # e.g., 'course_title', 'pitch', 'outcomes', etc.
        context = data.get('context', {})  # Existing answers for context
        
        # Check if OpenAI API key is configured
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            # Fallback to placeholder suggestions if OpenAI is not configured
            suggestions = {
                'course_title': [
                    f"Master {context.get('topic', 'Your Subject')}: A Complete Guide",
                    f"The Ultimate {context.get('topic', 'Course')} Course",
                    f"Transform Your {context.get('topic', 'Skills')} in 30 Days"
                ],
                'pitch': f"This course helps {context.get('audience', 'learners')} to {context.get('outcome', 'achieve their goals')} without {context.get('pain_point', 'struggling').lower()}.",
                'outcomes': [
                    f"Understand the fundamentals of {context.get('topic', 'the subject')}",
                    f"Apply {context.get('topic', 'key concepts')} in real-world scenarios",
                    f"Build confidence in {context.get('topic', 'your skills')}"
                ],
                'tone': ['Professional', 'Friendly', 'Inspiring', 'Authoritative'],
                'taglines': [
                    f"Transform your {context.get('topic', 'future')} today",
                    f"Learn {context.get('topic', 'skills')} the right way",
                    f"Your journey to {context.get('outcome', 'success')} starts here"
                ],
                'visual_style': 'modern',  # Returns one of: modern, classic, bold, elegant
                'course_description': f"This comprehensive course on {context.get('topic', 'your subject')} provides in-depth knowledge and practical skills. Through {context.get('pitch', 'engaging content')}, students will gain valuable insights and hands-on experience.",
                'main_transformation': f"After completing this course on {context.get('topic', 'your subject')}, students will experience a significant transformation in their understanding and capabilities. They'll be able to apply what they've learned in real-world scenarios.",
                'skills_gained': f"Problem-solving, Critical thinking, {context.get('topic', 'Subject-specific')} expertise, Analytical skills, Communication",
                'prerequisites': f"Students should have basic knowledge of {context.get('topic', 'the subject')} or be willing to learn. No advanced experience required for {context.get('audience', 'beginners')}.",
                'existing_content': f"For a course on {context.get('topic', 'your subject')}, typical existing materials might include presentation slides, video recordings, written documents, and supplementary notes that can be adapted for the course.",
                'materials_notes': f"Additional context about existing materials for {context.get('topic', 'the course')}: These materials provide a solid foundation and can be enhanced with new content to create a comprehensive learning experience.",
                'brand_description': f"Our brand represents expertise, clarity, and student success in {context.get('topic', 'education')}. We value practical learning, engagement, and helping students achieve their goals through high-quality course content.",
                'structure_notes': f"For this {context.get('format', 'course')} on {context.get('topic', 'your subject')}, the structure should be organized logically, with clear progression from basics to advanced concepts, ensuring students can follow along easily.",
                'media_notes': f"Media production for this course on {context.get('topic', 'your subject')} should focus on {context.get('on_camera', 'clear presentation')} with {context.get('audio_quality', 'good')} audio quality to ensure an engaging learning experience.",
                'third_party_content': f"For a course on {context.get('topic', 'your subject')}, third-party content may include stock images, royalty-free music, or licensed materials. All content should be properly licensed and attributed.",
                'required_permissions': f"Required permissions for this course include rights to use educational content, images, and any third-party materials. Licensing agreements should be in place before course launch.",
                'legal_notes': f"Legal considerations for this course on {context.get('topic', 'your subject')} include ensuring all content is original or properly licensed, protecting intellectual property, and complying with educational content regulations.",
                'revenue_goals': f"Our revenue goals for this course include generating sustainable income through {context.get('pricing', 'appropriate pricing')}, building a loyal student base, and creating opportunities for future course offerings.",
                'priority_features': f"For this course on {context.get('topic', 'your subject')}, priority features include clear explanations, practical exercises, and {context.get('urgency', 'quality')} content delivery to ensure student success.",
                'timeline_notes': f"Timeline considerations for this course include {context.get('urgency', 'balanced')} development pace, meeting the target launch date of {context.get('launch_date', 'TBD')}, and ensuring quality throughout the process.",
                'decision_makers': f"Decision-makers for this course on {context.get('topic', 'your subject')} may include course creators, subject matter experts, and stakeholders who need to review and approve the content before launch.",
                'review_criteria': f"Review criteria for this course should focus on accuracy of content, clarity of explanations, alignment with learning objectives, and overall quality of the {context.get('topic', 'course material')}.",
                'approval_notes': f"Approval process notes: The review process for this course involves {context.get('review_process', 'thorough evaluation')} to ensure all {context.get('criteria', 'quality standards')} are met before final approval and launch.",
                'file_descriptions': f"Uploaded files for this course may include course outlines, supplementary materials, reference documents, and resources that support the learning objectives and enhance the student experience.",
                'secret_notes': f"Additional context for this course on {context.get('topic', 'your subject')}: {context.get('pitch', 'This course aims to provide comprehensive learning')}. Special considerations include maintaining high quality standards and ensuring student engagement throughout."
            }
            result = suggestions.get(field_type, ['No suggestions available'])
            return JsonResponse({
                'success': True,
                'suggestions': result if isinstance(result, list) else [result],
                'field_type': field_type
            })
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Build prompts based on field type
        prompts = {
            'course_title': f"Generate 3 compelling course title suggestions for a course about: {context.get('topic', 'a subject')}. Target audience: {context.get('audience', 'learners')}. Make them engaging and clear. Return only the titles, one per line.",
            'pitch': f"Write a compelling one-sentence course pitch. Course topic: {context.get('topic', 'a subject')}. Target audience: {context.get('audience', 'learners')}. Format: 'This course helps [who] to [result] without [pain].'",
            'outcomes': f"Generate 3 specific, measurable learning outcomes for a course about: {context.get('topic', 'a subject')}. Course description: {context.get('pitch', '')}. Return only the outcomes, one per line.",
            'tone': f"Based on this brand description: {context.get('brand', '')}, suggest 4 appropriate tone words for the course content. Return only the words, comma-separated.",
            'taglines': f"Generate 3 catchy taglines for a course about: {context.get('topic', 'a subject')}. Tone: {context.get('tone', 'professional')}. Make them memorable and inspiring. Return only the taglines, one per line.",
            'visual_style': f"Based on this brand description: '{context.get('brand', '')}' and tone: '{context.get('tone', 'professional')}', recommend the best visual style. Choose ONE from: 'modern' (Modern & Minimalist), 'classic' (Classic & Traditional), 'bold' (Bold & Vibrant), or 'elegant' (Elegant & Refined). Return only the single word (modern, classic, bold, or elegant), nothing else.",
            'course_description': f"Write a detailed, engaging course description (3-5 sentences) for a course titled '{context.get('title', '')}' about {context.get('topic', 'a subject')}. The pitch is: {context.get('pitch', '')}. Make it compelling and informative.",
            'main_transformation': f"Describe the main transformation students will experience after completing a course about {context.get('topic', 'a subject')}. The course pitch is: {context.get('pitch', '')}. Learning outcomes include: {context.get('outcomes', '')}. Write 2-3 sentences describing the biggest change.",
            'skills_gained': f"List 5-7 key skills students will gain from a course about {context.get('topic', 'a subject')} with these learning outcomes: {context.get('outcomes', '')}. Return as a comma-separated list.",
            'prerequisites': f"Describe the prerequisites needed for a course about {context.get('topic', 'a subject')} targeting {context.get('audience', 'learners')}. Write 2-3 sentences about what students should know or have before starting.",
            'existing_content': f"Suggest a description of existing materials that might be available for a course about {context.get('topic', 'a subject')}. Write 2-3 sentences describing typical materials (slides, videos, documents, notes) that could be used.",
            'materials_notes': f"Write additional context notes about existing materials for a course about {context.get('topic', 'a subject')}. Existing content: {context.get('existing_content', '')}. Write 2-3 sentences with helpful context.",
            'brand_description': f"Write a compelling brand description (3-4 sentences) for a course creator teaching about {context.get('topic', 'a subject')}. The course pitch is: {context.get('pitch', '')}. Describe the brand personality, values, and style.",
            'structure_notes': f"Write course structure notes for a {context.get('format', 'video-based')} course about {context.get('topic', 'a subject')} with {context.get('length', 'medium')} length. Write 2-3 sentences with specific requirements or preferences.",
            'media_notes': f"Write media production notes for a course about {context.get('topic', 'a subject')}. On-camera preference: {context.get('on_camera', '')}. Audio quality: {context.get('audio_quality', 'standard')}. Write 2-3 sentences with requirements or concerns.",
            'third_party_content': f"Suggest a description of third-party content considerations for a course about {context.get('topic', 'a subject')} with content ownership: {context.get('ownership', '')}. Write 2-3 sentences about third-party content and licensing.",
            'required_permissions': f"Suggest required permissions/licenses for a course about {context.get('topic', 'a subject')}. Third-party content: {context.get('third_party', '')}. Write 2-3 sentences about permissions needed.",
            'legal_notes': f"Write legal notes for a course about {context.get('topic', 'a subject')} with content ownership: {context.get('ownership', '')}. Write 2-3 sentences about legal considerations or concerns.",
            'revenue_goals': f"Write revenue goals for a course about {context.get('topic', 'a subject')} with pricing model: {context.get('pricing', '')} and target price: {context.get('price', '')}. Write 2-3 sentences about revenue or business goals.",
            'priority_features': f"Suggest priority features for a course about {context.get('topic', 'a subject')} with urgency level: {context.get('urgency', 'medium')}. Write 2-3 sentences about what features are most important.",
            'timeline_notes': f"Write timeline notes for a course about {context.get('topic', 'a subject')} with urgency: {context.get('urgency', 'medium')} and launch date: {context.get('launch_date', 'TBD')}. Write 2-3 sentences about timeline requirements.",
            'decision_makers': f"Suggest a description of decision-makers/reviewers for a course about {context.get('topic', 'a subject')} with review process: {context.get('review_process', '')}. Write 2-3 sentences about who needs to review.",
            'review_criteria': f"Suggest review criteria for a course about {context.get('topic', 'a subject')} with review process: {context.get('review_process', '')}. Write 2-3 sentences about what aspects reviewers will check.",
            'approval_notes': f"Write approval notes for a course about {context.get('topic', 'a subject')} with review process: {context.get('review_process', '')} and criteria: {context.get('criteria', '')}. Write 2-3 sentences about approval requirements.",
            'file_descriptions': f"Suggest file descriptions for a course about {context.get('topic', 'a subject')}. Write 2-3 sentences describing what files might be uploaded and how they should be used.",
            'secret_notes': f"Write additional context notes for a course about {context.get('topic', 'a subject')} with pitch: {context.get('pitch', '')}. Write 3-4 sentences with any additional context, concerns, or special instructions."
        }
        
        prompt = prompts.get(field_type, f"Help me with: {field_type}")
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful course creation assistant. Provide concise, actionable suggestions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        # Parse response
        ai_response = response.choices[0].message.content.strip()
        
        # Format suggestions based on field type
        if field_type in ['course_title', 'outcomes', 'taglines']:
            suggestions = [line.strip() for line in ai_response.split('\n') if line.strip()][:3]
        elif field_type == 'tone':
            suggestions = [word.strip() for word in ai_response.split(',') if word.strip()][:4]
        elif field_type == 'visual_style':
            # Extract the style word (modern, classic, bold, or elegant)
            response_lower = ai_response.lower()
            if 'modern' in response_lower:
                suggestions = ['modern']
            elif 'classic' in response_lower:
                suggestions = ['classic']
            elif 'bold' in response_lower:
                suggestions = ['bold']
            elif 'elegant' in response_lower:
                suggestions = ['elegant']
            else:
                suggestions = ['modern']  # Default fallback
        else:
            suggestions = [ai_response]
        
        return JsonResponse({
            'success': True,
            'suggestions': suggestions,
            'field_type': field_type
        })
        
    except openai.OpenAIError as e:
        # Handle OpenAI API errors
        return JsonResponse({
            'success': False,
            'error': f'AI service error: {str(e)}'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ==================== DASHBOARD VIEWS ====================

@login_required
def dashboard_overview(request):
    """Main dashboard overview page"""
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    
    # KPI counts
    new_sessions = OnboardingSession.objects.filter(status='new').count()
    in_review = OnboardingSession.objects.filter(status='in_review').count()
    in_production = OnboardingSession.objects.filter(status='in_production').count()
    completed = OnboardingSession.objects.filter(status='completed').count()
    
    # New this week
    new_this_week = OnboardingSession.objects.filter(created_at__gte=week_ago).count()
    
    # Pipeline counts
    pipeline = {
        'new': OnboardingSession.objects.filter(status='new').count(),
        'in_review': OnboardingSession.objects.filter(status='in_review').count(),
        'needs_clarification': OnboardingSession.objects.filter(status='needs_clarification').count(),
        'approved': OnboardingSession.objects.filter(status='approved').count(),
        'in_production': OnboardingSession.objects.filter(status='in_production').count(),
        'completed': OnboardingSession.objects.filter(status='completed').count(),
    }
    
    # Recent activity (last 20)
    recent_sessions = OnboardingSession.objects.select_related('client', 'assignee').order_by('-updated_at')[:20]
    
    # Attention items
    old_review_sessions = OnboardingSession.objects.filter(
        status='in_review',
        updated_at__lt=now - timedelta(days=3)
    ).count()
    
    incomplete_sessions = OnboardingSession.objects.filter(
        Q(course_title='') | Q(course_title__isnull=True) | 
        Q(audience_summary='') | Q(main_outcomes='')
    ).count()
    
    context = {
        'new_sessions': new_sessions,
        'in_review': in_review,
        'in_production': in_production,
        'completed': completed,
        'new_this_week': new_this_week,
        'pipeline': pipeline,
        'recent_sessions': recent_sessions,
        'old_review_sessions': old_review_sessions,
        'incomplete_sessions': incomplete_sessions,
    }
    
    return render(request, 'myApp/dashboard/overview.html', context)


@login_required
def dashboard_sessions(request):
    """Sessions list page with filters"""
    sessions = OnboardingSession.objects.select_related('client', 'assignee').all()
    
    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        sessions = sessions.filter(status=status_filter)
    
    assignee_filter = request.GET.get('assignee', '')
    if assignee_filter:
        sessions = sessions.filter(assignee_id=assignee_filter)
    
    search_query = request.GET.get('q', '')
    if search_query:
        sessions = sessions.filter(
            Q(course_title__icontains=search_query) |
            Q(client__full_name__icontains=search_query) |
            Q(client__email__icontains=search_query) |
            Q(session_id__icontains=search_query)
        )
    
    # Date range
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        sessions = sessions.filter(created_at__gte=date_from)
    if date_to:
        sessions = sessions.filter(created_at__lte=date_to)
    
    # Ordering
    order_by = request.GET.get('order_by', '-created_at')
    sessions = sessions.order_by(order_by)
    
    # Convert to list for pagination
    sessions_list = list(sessions)
    
    # Pagination
    paginator = Paginator(sessions_list, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Recalculate and update progress for paginated sessions only (for performance)
    # This ensures progress is accurate and fixes any sessions with incorrect progress
    for session in page_obj:
        calculated_progress = session.calculate_progress(save=False)
        # Save if progress is different (to ensure database is accurate)
        if session.steps_completed != calculated_progress:
            session.steps_completed = calculated_progress
            session.save(update_fields=['steps_completed'])
    
    # Get all users for assignee filter
    from django.contrib.auth.models import User
    users = User.objects.filter(is_staff=True)
    
    context = {
        'sessions': page_obj,
        'status_filter': status_filter,
        'assignee_filter': assignee_filter,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'users': users,
        'status_choices': OnboardingSession.STATUS_CHOICES,
    }
    
    return render(request, 'myApp/dashboard/sessions.html', context)


@login_required
def dashboard_session_detail(request, session_id):
    """Session detail view"""
    session = get_object_or_404(
        OnboardingSession.objects.select_related('client', 'assignee'),
        id=session_id
    )
    
    # If session has no client but has meet_you data, try to create/link client
    if not session.client and session.meet_you:
        meet_you_data = session.meet_you
        if isinstance(meet_you_data, dict):
            email = meet_you_data.get('email', '').strip()
            full_name = meet_you_data.get('full_name', '').strip()
            if email and full_name:
                try:
                    client, created = Client.objects.get_or_create(
                        email=email,
                        defaults={
                            'full_name': full_name,
                            'brand_name': meet_you_data.get('brand_name', ''),
                            'phone': meet_you_data.get('phone', ''),
                            'website': meet_you_data.get('website', ''),
                        }
                    )
                    if not created:
                        # Update existing client
                        client.full_name = full_name
                        if meet_you_data.get('brand_name'):
                            client.brand_name = meet_you_data.get('brand_name', '')
                        if meet_you_data.get('phone'):
                            client.phone = meet_you_data.get('phone', '')
                        if meet_you_data.get('website'):
                            client.website = meet_you_data.get('website', '')
                        client.save()
                    session.client = client
                    session.save(update_fields=['client'])
                except Exception as e:
                    # If client creation fails, just continue without it
                    pass
    
    # Get related data
    notes = session.notes.select_related('author').all()
    tasks = session.tasks.select_related('assignee').all()
    tags = session.tags.select_related('tag').all()
    
    # Calculate and save progress (in case it's out of sync)
    progress = session.calculate_progress(save=True)
    
    # Get all users for assignee dropdown
    from django.contrib.auth.models import User
    users = User.objects.filter(is_staff=True)
    
    # Prepare step data for template
    step_data = {}
    step_data['meet_you'] = session.meet_you or {}
    step_data['course_idea'] = session.course_idea or {}
    step_data['transformation_outcomes'] = session.transformation_outcomes or {}
    step_data['existing_materials'] = session.existing_materials or {}
    step_data['brand_vibe'] = session.brand_vibe or {}
    step_data['course_structure'] = session.course_structure or {}
    step_data['media_content'] = session.media_content or {}
    step_data['legal_rights'] = session.legal_rights or {}
    step_data['platform_money'] = session.platform_money or {}
    step_data['timelines_priorities'] = session.timelines_priorities or {}
    step_data['reviews_decision_makers'] = session.reviews_decision_makers or {}
    step_data['final_uploads'] = session.final_uploads or {}
    
    context = {
        'session': session,
        'notes': notes,
        'tasks': tasks,
        'tags': tags,
        'progress': progress,
        'users': users,
        'step_data': step_data,
        'step_names': [
            ('meet_you', '01 · Meet You', 'Core contact & creator profile'),
            ('course_idea', '02 · Course Idea', 'Core concept & vision'),
            ('transformation_outcomes', '03 · Transformation & Outcomes', 'Student transformation & skills'),
            ('existing_materials', '04 · What You Already Have', 'Existing assets & materials'),
            ('brand_vibe', '05 · Brand & Vibe', 'Brand personality & style'),
            ('course_structure', '06 · Course Structure', 'Structure & interactivity'),
            ('media_content', '07 · Your Face & Voice', 'Media production preferences'),
            ('legal_rights', '08 · Legal & Rights', 'Rights, permissions & legal'),
            ('platform_money', '09 · Platform & Money', 'Platforms, pricing & revenue'),
            ('timelines_priorities', '10 · Timelines & Priorities', 'Timeline & priority features'),
            ('reviews_decision_makers', '11 · Reviews & Decision-Makers', 'Reviewers & approval process'),
            ('final_uploads', '12 · Final Uploads', 'Files & secret notes'),
        ],
    }
    
    return render(request, 'myApp/dashboard/session_detail.html', context)


@login_required
@require_http_methods(["POST"])
def dashboard_update_status(request, session_id):
    """Update session status"""
    session = get_object_or_404(OnboardingSession, id=session_id)
    new_status = request.POST.get('status', '')
    
    if new_status in dict(OnboardingSession.STATUS_CHOICES):
        session.status = new_status
        session.save(update_fields=['status', 'updated_at'])
        return JsonResponse({'success': True, 'status': new_status})
    
    return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)


@login_required
@require_http_methods(["POST"])
def dashboard_assign(request, session_id):
    """Assign session to user"""
    session = get_object_or_404(OnboardingSession, id=session_id)
    assignee_id = request.POST.get('assignee_id', '')
    
    if assignee_id:
        from django.contrib.auth.models import User
        try:
            assignee = User.objects.get(id=assignee_id)
            session.assignee = assignee
            session.save(update_fields=['assignee', 'updated_at'])
            return JsonResponse({'success': True, 'assignee': assignee.username})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    else:
        session.assignee = None
        session.save(update_fields=['assignee', 'updated_at'])
        return JsonResponse({'success': True, 'assignee': None})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
@require_http_methods(["POST"])
def dashboard_add_note(request, session_id):
    """Add internal note to session"""
    session = get_object_or_404(OnboardingSession, id=session_id)
    content = request.POST.get('content', '')
    note_type = request.POST.get('note_type', 'general')
    
    if content:
        note = InternalNote.objects.create(
            session=session,
            author=request.user,
            note_type=note_type,
            content=content
        )
        return JsonResponse({
            'success': True,
            'note': {
                'id': note.id,
                'content': note.content,
                'author': note.author.username if note.author else 'Unknown',
                'note_type': note.get_note_type_display(),
                'created_at': note.created_at.isoformat(),
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Content required'}, status=400)


@login_required
@require_http_methods(["POST"])
def dashboard_generate_ai_summary(request, session_id):
    """Generate AI summary for session"""
    session = get_object_or_404(OnboardingSession, id=session_id)
    
    # Build context from session data
    all_data = session.get_all_data()
    context_text = json.dumps(all_data, indent=2)
    
    prompt = f"""Based on this course onboarding data, create a concise 1-2 paragraph summary that includes:
- Who the course is for (target audience)
- Main promise/transformation
- Format and structure
- Key outcomes
- Any risks or questions if fields look weak

Onboarding Data:
{context_text}

Provide a professional, clear summary:"""
    
    try:
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a course architect assistant. Create clear, professional summaries of course blueprints."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            summary = response.choices[0].message.content.strip()
        else:
            summary = f"Course Blueprint Summary\n\nTarget Audience: {session.audience_summary or 'Not specified'}\n\nMain Transformation: {session.main_outcomes or 'Not specified'}\n\nCourse Title: {session.course_title or 'Not specified'}\n\n[AI summary generation requires OPENAI_API_KEY]"
        
        session.ai_summary = summary
        session.save(update_fields=['ai_summary', 'updated_at'])
        
        return JsonResponse({'success': True, 'summary': summary})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def dashboard_export_csv(request):
    """Export filtered sessions to CSV"""
    sessions = OnboardingSession.objects.select_related('client', 'assignee').all()
    
    # Apply same filters as sessions list
    status_filter = request.GET.get('status', '')
    if status_filter:
        sessions = sessions.filter(status=status_filter)
    
    search_query = request.GET.get('q', '')
    if search_query:
        sessions = sessions.filter(
            Q(course_title__icontains=search_query) |
            Q(client__full_name__icontains=search_query) |
            Q(client__email__icontains=search_query)
        )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sessions_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Client', 'Email', 'Course Title', 'Status', 'Assignee',
        'Steps Completed', 'Created At', 'Updated At'
    ])
    
    for session in sessions:
        writer.writerow([
            session.id,
            session.client.full_name if session.client else 'N/A',
            session.client.email if session.client else 'N/A',
            session.course_title or 'N/A',
            session.get_status_display(),
            session.assignee.username if session.assignee else 'Unassigned',
            session.steps_completed,
            session.created_at,
            session.updated_at,
        ])
    
    return response