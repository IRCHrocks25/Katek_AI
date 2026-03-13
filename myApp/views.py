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
import re
import uuid
import csv
from .models import OnboardingSession, Client, Tag, SessionTag, InternalNote, Task
import openai


def home(request):
    """Homepage view - uses database content if available"""
    from .content_helpers import get_website_content_from_db
    
    # Get content from database
    website_content = get_website_content_from_db()
    
    context = {
        'content': website_content,
    }
    
    return render(request, 'myApp/home.html', context)


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
    import logging
    logger = logging.getLogger(__name__)
    logger.info('[KaTek] onboarding_save called')
    try:
        try:
            data = json.loads(request.body)
            logger.info('[KaTek] Parsed JSON, submit=%s, steps=%s', data.get('submit'), list(data.get('steps', {}).keys()) if data.get('steps') else 'none')
        except json.JSONDecodeError as e:
            logger.error('[KaTek] JSON decode error: %s', e)
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
                        session.audience_summary = step_data.get('target_audience', '') or step_data.get('ideal_student', '') or session.audience_summary
                    elif step_key == 'transformation_outcomes' and step_data:
                        outcomes = step_data.get('learning_outcomes', '') or step_data.get('transformation', '')
                        if isinstance(outcomes, str):
                            session.main_outcomes = outcomes or session.main_outcomes
                        elif isinstance(outcomes, list):
                            session.main_outcomes = '\n'.join(outcomes) or session.main_outcomes
                    elif step_key == 'platform_money' and step_data:
                        session.access_model = step_data.get('pricing_model', '') or step_data.get('price_point', '') or session.access_model
                    
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
            
            # Add the step JSON fields that were updated (critical - without this, step data is never saved!)
            for step_key in saved_steps:
                if step_key in step_mapping:
                    update_fields.append(step_mapping[step_key])
            
            # Add denormalized fields if they were updated
            if any(step_key in ['course_idea', 'transformation_outcomes', 'platform_money'] for step_key in saved_steps):
                update_fields.extend(['course_title', 'audience_summary', 'main_outcomes', 'access_model'])
            
            if data.get('submit', False):
                update_fields.extend(['status', 'submitted_at'])
            
            session.save(update_fields=list(dict.fromkeys(update_fields)))  # dedupe while preserving order
        except Exception as save_error:
            logger.exception('[KaTek] Save failed: %s', save_error)
            return JsonResponse({
                'success': False,
                'error': f'Failed to save session: {str(save_error)}',
                'saved_steps': saved_steps,
                'errors': errors
            }, status=400)
        
        # Return success even if some steps had errors (partial save)
        logger.info('[KaTek] Save success, session_id=%s, saved_steps=%s', session.session_id, saved_steps)
        response_data = {
            'success': True,
            'session_id': session.session_id,
            'message': 'Data saved successfully',
            'saved_steps': saved_steps
        }
        
        if errors:
            response_data['warnings'] = errors
            logger.warning('[KaTek] Save had warnings: %s', errors)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_message = str(e)
        logger = logging.getLogger(__name__)
        logger.exception('[KaTek] onboarding_save unhandled: %s', e)
        
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
def onboarding_upload(request):
    """Upload file to Cloudinary, return URL for onboarding form"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)
        file_obj = request.FILES['file']
        field = request.POST.get('field', 'general')  # bkit, logo, mats
        from .utils.cloudinary_utils import upload_file_to_cloudinary
        folder = f'katek_ai/onboarding/{field}'
        result = upload_file_to_cloudinary(file_obj, folder=folder, resource_type='auto')
        url = result.get('secure_url') or result.get('url', '')
        if not url:
            return JsonResponse({'success': False, 'error': 'Upload succeeded but no URL returned'}, status=500)
        logger.info('[KaTek] File uploaded to Cloudinary: %s', url[:80])
        return JsonResponse({'success': True, 'url': url})
    except Exception as e:
        logger.exception('[KaTek] onboarding_upload error: %s', e)
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def _clean_subject(val, max_len=60):
    """Extract a single-line, trimmed subject from context (avoids multi-line blobs in suggestions)."""
    if not val or not isinstance(val, str):
        return ''
    first_line = val.strip().split('\n')[0].strip()
    return first_line[:max_len] if first_line else ''


@csrf_exempt
@require_http_methods(["POST"])
def onboarding_ai_help(request):
    """API endpoint for AI assistance on specific fields"""
    try:
        data = json.loads(request.body)
        field_type = data.get('field_type') or data.get('field') or ''
        context = data.get('context') or data.get('ctx') or {}
        if not isinstance(context, dict):
            context = {}

        def _ideal_student_fallback(ctx):
            what = (ctx.get('what_you_do') or '').strip()
            aliases = (ctx.get('aliases') or '').strip()
            trans = (ctx.get('transformation') or '').strip()
            if what or aliases:
                hint = aliases or _clean_subject(what)[:50] or 'your niche'
                return f"People who want to build confidence and clarity in their goals — often overwhelmed, ready for change, and looking for a clear path. Based on your focus ({hint}), they may be professionals, entrepreneurs, or anyone seeking practical, jargon-free guidance."
            if trans:
                return f"Learners who want to {trans}. They're motivated, ready to take action, and looking for step-by-step support."
            return "People who want to learn and grow — motivated, ready for change, and looking for clear, practical guidance. Be specific about age, profession, and pain points when you customize this."

        # Check if OpenAI API key is configured
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            # Fallback to placeholder suggestions if OpenAI is not configured
            subject = _clean_subject(context.get('expertise') or context.get('topic')) or 'Your Subject'
            suggestions = {
                'course_title': [
                    f"Master {subject}: A Complete Guide",
                    f"The Ultimate {subject} Course",
                    f"Transform Your {subject} Skills in 30 Days"
                ],
                'pitch': f"This course helps {context.get('audience') or 'learners'} to {context.get('outcome') or 'achieve their goals'} without {str(context.get('pain_point') or 'struggling').lower()}.",
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
            # Welcome Kit field fallbacks
            topic = context.get('course_title') or context.get('topic') or 'your course'
            aliases = (context.get('aliases') or '').strip()
            brand = (context.get('brand_name') or '').strip()
            hint = aliases or brand
            if hint:
                suggestions['what_you_do'] = [f"As {hint}, I help people build confidence, clarity, and real results in their goals — in plain language, no jargon."]
            else:
                suggestions['what_you_do'] = [f"I help {context.get('ideal_student', 'learners')} to {context.get('transformation', 'achieve their goals')}."]
            suggestions['ideal_student'] = [_ideal_student_fallback(context)]
            suggestions['audience'] = [f"Email list, social following, and community aligned with {topic}."]
            suggestions['transformation'] = [f"Before: overwhelmed and unsure where to start. After: confident, clear on next steps, and equipped with practical tools to take action."]
            suggestions['modules'] = [f"1. Foundations\n2. Core concepts\n3. Practice\n4. Advanced\n5. Next steps"]
            suggestions['logo_brief'] = [f"Professional, clean, aligned with {topic}."]
            suggestions['must_include'] = [f"Key frameworks, signature stories, and practical exercises."]
            suggestions['video_setup'] = [f"Clear audio, good lighting, comfortable recording environment."]
            suggestions['feature_notes'] = [f"Analytics, certificates, and engagement features."]
            suggestions['success'] = [f"50+ enrolled students in the first launch, $25k+ revenue, positive feedback, and a growing email list. Establishing authority in the niche and creating a repeatable launch system."]
            suggestions['concerns'] = [f"I want it to feel authentic to my voice. Worried about the tech being overwhelming. Concerned I won't have enough time to review everything. Want to make sure students actually get results."]
            suggestions['prev_notes'] = [f"Learned from past launches; iterating on what worked."]
            suggestions['anything_else'] = [f"Ready to collaborate and create something valuable."]
            # Add missing field types used by the onboarding form
            suggestions['expertise'] = [
                f"{context.get('topic', 'Your subject')} fundamentals and practical applications",
                f"Professional {context.get('topic', 'expertise')} with real-world experience",
                f"Advanced {context.get('topic', 'skills')} and best practices"
            ]
            
            result = suggestions.get(field_type, [f"Enter your {field_type.replace('_', ' ')} here."])
            return JsonResponse({
                'success': True,
                'suggestions': result if isinstance(result, list) else [result],
                'field_type': field_type
            })
        
        # Helper to get fallback suggestions when OpenAI fails
        def get_fallback_suggestions():
            subject = _clean_subject(context.get('expertise') or context.get('topic')) or 'Your Subject'
            fallback = {
                'course_title': [f"Master {subject}: A Complete Guide", f"The Ultimate {subject} Course", f"Transform Your {subject} Skills"],
                'pitch': f"This course helps {context.get('audience', 'learners')} to {context.get('outcome', 'achieve their goals')}.",
                'outcomes': [f"Understand {context.get('topic', 'the subject')}", f"Apply key concepts in practice", f"Build confidence in your skills"],
                'expertise': [f"{context.get('topic', 'Your subject')} fundamentals", f"Professional expertise in {context.get('topic', 'this area')}"],
                'audience': f"{context.get('audience', 'Learners')} who want to improve in {context.get('topic', 'this area')}.",
                'main_transformation': f"Students will gain practical skills in {context.get('topic', 'the subject')} and apply them confidently.",
                'existing_content': f"Typical materials: slides, recordings, documents. Adapt for {context.get('topic', 'your course')}.",
                'brand_description': f"Expert, clear, student-focused. Professional yet approachable style for {context.get('topic', 'education')}.",
                'structure_notes': f"Logical progression from basics to advanced. Modules with clear lessons for {context.get('topic', 'the course')}.",
                'media_notes': f"Clear presentation with good audio. Focus on engagement for {context.get('topic', 'learners')}.",
                'legal_notes': f"Original or properly licensed content. Protect IP and comply with regulations for {context.get('topic', 'education')}.",
                'revenue_goals': f"Sustainable income through appropriate pricing. Build student base for {context.get('topic', 'this course')}.",
                'timeline_notes': f"Balanced development pace. Target launch aligned with quality for {context.get('topic', 'the course')}.",
                'decision_makers': f"Course creator, subject experts, stakeholders review before launch.",
                'secret_notes': f"Additional context for {context.get('topic', 'this course')}. Special considerations for quality and engagement.",
                'what_you_do': [f"As {(context.get('aliases') or context.get('brand_name') or '').strip() or 'a coach'}, I help people build confidence, clarity, and real results — in plain language, no jargon."],
                'ideal_student': [_ideal_student_fallback(context)],
                'transformation': [f"Before: overwhelmed and unsure where to start. After: confident, clear on next steps, and equipped with practical tools to take action."],
                'modules': [f"1. Foundations\n2. Core concepts\n3. Practice\n4. Advanced\n5. Next steps"],
                'logo_brief': [f"Professional, clean, aligned with {context.get('course_title', 'your course')}."],
                'must_include': [f"Key frameworks, signature stories, and practical exercises."],
                'video_setup': [f"Clear audio, good lighting, comfortable recording environment."],
                'feature_notes': [f"Analytics, certificates, and engagement features."],
                'success': [f"50+ enrolled students in the first launch, $25k+ revenue, positive feedback, and a growing email list. Establishing authority in the niche and creating a repeatable launch system."],
                'concerns': [f"I want it to feel authentic to my voice. Worried about the tech being overwhelming. Concerned I won't have enough time to review everything. Want to make sure students actually get results."],
                'prev_notes': [f"Learned from past launches; iterating on what worked."],
                'anything_else': [f"Ready to collaborate and create something valuable."],
            }
            result = fallback.get(field_type, [f"Enter your {field_type.replace('_', ' ')}."])
            return result if isinstance(result, list) else [result]
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Build prompts based on field type
        prompts = {
            'expertise': f"Suggest 3 brief expertise descriptions for someone teaching: {context.get('topic', 'a subject')}. Return only the descriptions, one per line. Each should be 5-10 words.",
            'audience': f"Write a one-sentence target audience description for a course about: {context.get('topic', 'a subject')} titled '{context.get('title', '')}'. Be specific about who would benefit.",
            'course_title': f"Generate exactly 3 compelling course title suggestions. The creator's expertise/subject: {_clean_subject(context.get('expertise') or context.get('topic')) or 'their field'}. Their role: {_clean_subject(context.get('role')) or 'educator'}. Target audience: {_clean_subject(context.get('audience')) or 'learners'}. IMPORTANT: Return ONLY 3 titles, one per line, no numbers or bullets. Each title must be a complete, standalone course name.",
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
            'secret_notes': f"Write additional context notes for a course about {context.get('topic', 'a subject')} with pitch: {context.get('pitch', '')}. Write 3-4 sentences with any additional context, concerns, or special instructions.",
            # Welcome Kit / 7-section onboarding fields (use full context for consistency)
            'what_you_do': f"""Write a clear, confident 2-3 sentence description of what this course creator does. Use this context:
- Name/brand: {context.get('brand_name', '') or context.get('full_name', '')}
- Other names/aliases: {context.get('aliases', '')}
- Course title (if known): {context.get('course_title', '')}
If aliases hint at their niche (e.g. "The Money Mentor" = finance/coaching), use that. Format: "I help [who] to [what]..." — conversational, no jargon. Write a COMPLETE 2-3 sentences. Never end mid-sentence.""",
            'ideal_student': f"""Describe the ideal student/client in 3-4 complete sentences. Use this context:
- What the creator does: {context.get('what_you_do', '')}
- Aliases/brand: {context.get('aliases', '')} {context.get('brand_name', '')}
- Course: {context.get('course_title', '')}
Include: who they are (age, profession), their biggest struggles, what they want to achieve. Write a FULL, actionable description. Never end with "who want to" or "who need to" — always finish the thought. Example: "Female entrepreneurs 28-45, overwhelmed by systems, want clarity and confidence." """,
            'audience': f"List this creator's existing audience/channels. Based on: brand {context.get('brand_name', '')}, course {context.get('course_title', '')}, platforms {context.get('platforms', '')}. Format: Email list: X · Instagram: X · etc. Return a concise list.",
            'transformation': f"""Describe the core transformation in 2-3 complete sentences. Creator does: {context.get('what_you_do', '')}. Ideal student: {context.get('ideal_student', '')}. Course: {context.get('course_title', '')}.
Format: "Before: [specific struggle]. After: [specific outcome]." Be concrete — no vague endings. Always complete every sentence.""",
            'modules': f"Generate 5-7 module/pillar topics for course '{context.get('course_title', '')}'. Transformation: {context.get('transformation', '')}. Ideal student: {context.get('ideal_student', '')}. Content formats they want: {context.get('content_formats', '')}. Return as a numbered list, one per line. Logical progression from foundation to advanced.",
            'logo_brief': f"Write a brand/logo brief. Brand: {context.get('brand_name', '')}. Course: {context.get('course_title', '')}. Colours: {context.get('brand_colors', '')}. Visual style: {context.get('visual_style', '')}. References: {context.get('inspiration', '')}. Fonts: {context.get('font_heading', '')} / {context.get('font_body', '')}. Describe tone, colours, feel. 3-4 sentences.",
            'must_include': f"For course '{context.get('course_title', '')}' (transformation: {context.get('transformation', '')}), suggest key content that must be included. What they do: {context.get('what_you_do', '')}. Materials they have: {context.get('materials_providing', '')}. List 3-5 specific items: frameworks, stories, techniques.",
            'video_setup': f"Suggest video production notes. Course: {context.get('course_title', '')}. Creator style: {context.get('what_you_do', '')}. Content formats: {context.get('content_formats', '')}. Materials: {context.get('materials_providing', '')}. Describe equipment, environment, support needed. 2-3 sentences.",
            'feature_notes': f"For course '{context.get('course_title', '')}' targeting {context.get('ideal_student', '')}, suggest platform features. Price: {context.get('price_point', '')}. Features they enabled: {context.get('features_enabled', '')}. Deliverables needed: {context.get('deliverables', '')}. List 3-5 specific feature needs.",
            'success': f"Define success for course '{context.get('course_title', '')}'. Transformation: {context.get('transformation', '')}. Be specific: enrolments, revenue, timeline. 2-3 sentences.",
            'concerns': f"Anticipate concerns for a creator building '{context.get('course_title', '')}'. Based on: {context.get('what_you_do', '')}, {context.get('ideal_student', '')}. List 2-4 common anxieties, empathetically.",
            'prev_notes': f"Reflect on past course experience. Context: {context.get('course_title', '')}, {context.get('what_you_do', '')}. Have they created a course before? {context.get('prev_course', '')}. Suggest what might have worked/didn't work. 2-3 sentences.",
            'anything_else': f"Suggest additional context for course '{context.get('course_title', '')}'. Creator: {context.get('brand_name', '')}. Response time: {context.get('response_time', '')}. Involvement: {context.get('involvement', '')}. Revision preferences: {context.get('revisions', '')}. So far: transformation={context.get('transformation', '')}, success={context.get('success', '')}, concerns={context.get('concerns', '')}. What else might matter? 2-3 sentences.",
        }
        
        prompt = prompts.get(field_type, f"Based on this course context — title: {context.get('course_title', '')}, creator: {context.get('brand_name', '')}, ideal student: {context.get('ideal_student', '')} — help with: {field_type}. Keep it consistent with the overall vision. Return 2-4 sentences.")
        
        try:
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful course creation assistant. Always return complete, usable suggestions. Never truncate or end mid-sentence."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.5
            )
            ai_response = response.choices[0].message.content.strip()
            # Reject obviously incomplete or generic responses
            r = ai_response.rstrip()
            incomplete_endings = (' to.', ' to ', ' want to.', ' who want to.', ' who need to.')
            is_incomplete = (len(r) < 40 or
                            any(r.endswith(e) for e in incomplete_endings) or
                            (len(r) < 80 and r.count('.') == 0))
            if is_incomplete:
                suggestions = get_fallback_suggestions()
                return JsonResponse({'success': True, 'suggestions': suggestions, 'field_type': field_type})
        except (openai.OpenAIError, Exception) as e:
            # Fall back to placeholder suggestions when API fails (invalid key, rate limit, network, etc.)
            suggestions = get_fallback_suggestions()
            return JsonResponse({
                'success': True,
                'suggestions': suggestions,
                'field_type': field_type
            })
        
        # Format suggestions based on field type
        if field_type in ['course_title', 'outcomes', 'taglines', 'expertise']:
            lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
            # Strip numbered prefixes (1. 2. 1) 2) etc.)
            suggestions = [re.sub(r'^\d+[\.\)]\s*', '', line).strip() for line in lines[:3]]
            suggestions = [s for s in suggestions if len(s) > 2]
            if not suggestions:
                suggestions = [ai_response.strip()[:200]]  # fallback to first 200 chars
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