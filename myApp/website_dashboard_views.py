"""
Website Dashboard Views - For managing website content
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import transaction
import json

from .models import (
    MediaAsset, SEO, WebsiteHero, WebsiteSection, 
    WebsiteTestimonial, WebsiteFooter
)
from .utils.cloudinary_utils import upload_to_cloudinary


@login_required
def website_dashboard_home(request):
    """Main website dashboard homepage"""
    # Get counts
    total_images = MediaAsset.objects.count()
    active_sections = WebsiteSection.objects.filter(is_active=True).count()
    total_testimonials = WebsiteTestimonial.objects.filter(is_active=True).count()
    
    # Get recent images
    recent_images = MediaAsset.objects.all()[:6]
    
    # Get sections status
    sections = WebsiteSection.objects.all()
    
    context = {
        'total_images': total_images,
        'active_sections': active_sections,
        'total_testimonials': total_testimonials,
        'recent_images': recent_images,
        'sections': sections,
    }
    
    return render(request, 'myApp/website_dashboard/index.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def website_upload_image(request):
    """Upload single or multiple images to Cloudinary"""
    try:
        # Handle multiple images
        images = request.FILES.getlist('images[]') or request.FILES.getlist('image')
        
        if not images:
            return JsonResponse({'success': False, 'error': 'No image files provided'}, status=400)
        
        folder = request.POST.get('folder', 'katek_ai/uploads')
        uploaded_assets = []
        errors = []
        
        for idx, image_file in enumerate(images):
            try:
                # Upload to Cloudinary
                upload_result = upload_to_cloudinary(image_file, folder=folder)
                
                # Get title from form or use filename
                title = request.POST.get(f'title_{idx}', '') or request.POST.get('title', '') or image_file.name
                
                # Save to database
                media_asset = MediaAsset.objects.create(
                    title=title,
                    cloudinary_url=upload_result['secure_url'],
                    cloudinary_public_id=upload_result['public_id'],
                    original_url=upload_result['original_url'],
                    web_url=upload_result['web_url'],
                    thumbnail_url=upload_result['thumbnail_url'],
                    folder=folder,
                    width=upload_result['width'],
                    height=upload_result['height'],
                    file_size=upload_result['bytes'],
                    format=upload_result['format'],
                )
                
                uploaded_assets.append({
                    'id': media_asset.id,
                    'title': media_asset.title,
                    'url': media_asset.cloudinary_url,
                    'web_url': media_asset.web_url,
                    'thumbnail_url': media_asset.thumbnail_url,
                    'public_id': media_asset.cloudinary_public_id,
                    'width': media_asset.width,
                    'height': media_asset.height,
                })
            except Exception as e:
                errors.append(f'{image_file.name}: {str(e)}')
        
        return JsonResponse({
            'success': True,
            'assets': uploaded_assets,
            'uploaded_count': len(uploaded_assets),
            'errors': errors if errors else None
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def website_gallery(request):
    """Image gallery page"""
    images = MediaAsset.objects.all()
    
    # Filter by folder if provided
    folder_filter = request.GET.get('folder', '')
    if folder_filter:
        images = images.filter(folder=folder_filter)
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        images = images.filter(title__icontains=search_query)
    
    images = images.order_by('-created_at')
    
    # Get unique folders
    folders = MediaAsset.objects.values_list('folder', flat=True).distinct()
    
    context = {
        'images': images,
        'folders': folders,
        'folder_filter': folder_filter,
        'search_query': search_query,
    }
    
    return render(request, 'myApp/website_dashboard/gallery.html', context)


@login_required
def website_gallery_api(request):
    """API endpoint to get gallery images as JSON"""
    images = MediaAsset.objects.all().order_by('-created_at')
    
    # Filter by folder if provided
    folder_filter = request.GET.get('folder', '')
    if folder_filter:
        images = images.filter(folder=folder_filter)
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        images = images.filter(title__icontains=search_query)
    
    # Limit results for performance
    limit = int(request.GET.get('limit', 100))
    images = images[:limit]
    
    images_data = [{
        'id': img.id,
        'title': img.title,
        'url': img.cloudinary_url,
        'web_url': img.web_url,
        'thumbnail_url': img.thumbnail_url,
        'original_url': img.original_url,
        'width': img.width,
        'height': img.height,
        'format': img.format,
        'folder': img.folder,
    } for img in images]
    
    return JsonResponse({
        'success': True,
        'images': images_data,
        'count': len(images_data)
    })


@login_required
def website_seo_edit(request):
    """Edit SEO settings"""
    seo, created = SEO.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        seo.page_title = request.POST.get('page_title', '')
        seo.meta_description = request.POST.get('meta_description', '')
        seo.meta_keywords = request.POST.get('meta_keywords', '')
        seo.og_title = request.POST.get('og_title', '')
        seo.og_description = request.POST.get('og_description', '')
        seo.og_image_url = request.POST.get('og_image_url', '')
        seo.twitter_card = request.POST.get('twitter_card', 'summary_large_image')
        seo.canonical_url = request.POST.get('canonical_url', '')
        seo.save()
        
        messages.success(request, 'SEO settings updated successfully!')
        return redirect('website_dashboard:seo_edit')
    
    context = {
        'seo': seo,
    }
    
    return render(request, 'myApp/website_dashboard/seo_edit.html', context)


@login_required
def website_hero_edit(request):
    """Edit Hero section"""
    hero, created = WebsiteHero.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        hero.pill_label = request.POST.get('pill_label', '')
        hero.main_headline = request.POST.get('main_headline', '')
        hero.subheadline = request.POST.get('subheadline', '')
        hero.primary_cta_text = request.POST.get('primary_cta_text', '')
        hero.primary_cta_link = request.POST.get('primary_cta_link', '')
        hero.secondary_cta_text = request.POST.get('secondary_cta_text', '')
        hero.secondary_cta_link = request.POST.get('secondary_cta_link', '')
        hero.background_image_url = request.POST.get('background_image_url', '')
        hero.dashboard_image_url = request.POST.get('dashboard_image_url', '')
        hero.is_active = request.POST.get('is_active') == 'on'
        hero.save()
        
        messages.success(request, 'Hero section updated successfully!')
        return redirect('website_dashboard:hero_edit')
    
    context = {
        'hero': hero,
    }
    
    return render(request, 'myApp/website_dashboard/hero_edit.html', context)


@login_required
def website_section_edit(request, section_type):
    """Edit a website section - creates if doesn't exist"""
    # Validate section type
    valid_section_types = [choice[0] for choice in WebsiteSection.SECTION_TYPES]
    if section_type not in valid_section_types:
        messages.error(request, f'Invalid section type: {section_type}')
        return redirect('website_dashboard:home')
    
    # Get or create the section
    section, created = WebsiteSection.objects.get_or_create(
        section_type=section_type,
        defaults={
            'title': '',
            'subtitle': '',
            'description': '',
            'is_active': True,
            'sort_order': 0,
        }
    )
    
    if request.method == 'POST':
        section.title = request.POST.get('title', '')
        section.subtitle = request.POST.get('subtitle', '')
        section.description = request.POST.get('description', '')
        section.background_image_url = request.POST.get('background_image_url', '')
        section.is_active = request.POST.get('is_active') == 'on'
        
        # Handle JSON content
        content_data = {}
        for key, value in request.POST.items():
            if key.startswith('content_'):
                content_key = key.replace('content_', '')
                content_data[content_key] = value
        
        if content_data:
            section.content = content_data
        
        section.save()
        
        messages.success(request, f'{section.get_section_type_display()} updated successfully!')
        return redirect('website_dashboard:section_edit', section_type=section_type)
    
    context = {
        'section': section,
    }
    
    return render(request, 'myApp/website_dashboard/section_edit.html', context)


@login_required
def website_testimonials_list(request):
    """List all testimonials"""
    testimonials = WebsiteTestimonial.objects.all().order_by('sort_order', '-created_at')
    
    context = {
        'testimonials': testimonials,
    }
    
    return render(request, 'myApp/website_dashboard/testimonials_list.html', context)


@login_required
def website_testimonial_edit(request, testimonial_id=None):
    """Create or edit a testimonial"""
    if testimonial_id:
        testimonial = get_object_or_404(WebsiteTestimonial, id=testimonial_id)
    else:
        testimonial = None
    
    if request.method == 'POST':
        if testimonial:
            testimonial.quote = request.POST.get('quote', '')
            testimonial.author_name = request.POST.get('author_name', '')
            testimonial.author_title = request.POST.get('author_title', '')
            testimonial.avatar_url = request.POST.get('avatar_url', '')
            testimonial.sort_order = int(request.POST.get('sort_order', 0))
            testimonial.is_active = request.POST.get('is_active') == 'on'
            testimonial.save()
        else:
            testimonial = WebsiteTestimonial.objects.create(
                quote=request.POST.get('quote', ''),
                author_name=request.POST.get('author_name', ''),
                author_title=request.POST.get('author_title', ''),
                avatar_url=request.POST.get('avatar_url', ''),
                sort_order=int(request.POST.get('sort_order', 0)),
                is_active=request.POST.get('is_active') == 'on',
            )
        
        messages.success(request, 'Testimonial saved successfully!')
        return redirect('website_dashboard:testimonials_list')
    
    context = {
        'testimonial': testimonial,
    }
    
    return render(request, 'myApp/website_dashboard/testimonial_edit.html', context)


@login_required
@require_http_methods(["POST"])
def website_testimonial_delete(request, testimonial_id):
    """Delete a testimonial"""
    testimonial = get_object_or_404(WebsiteTestimonial, id=testimonial_id)
    testimonial.delete()
    messages.success(request, 'Testimonial deleted successfully!')
    return redirect('website_dashboard:testimonials_list')


@login_required
def website_footer_edit(request):
    """Edit Footer content"""
    footer, created = WebsiteFooter.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        footer.copyright_text = request.POST.get('copyright_text', '')
        
        # Handle social links
        social_links = {}
        platforms = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube']
        for platform in platforms:
            url = request.POST.get(f'social_{platform}', '')
            if url:
                social_links[platform] = url
        footer.social_links = social_links
        
        # Handle footer links (simplified - can be enhanced)
        footer.save()
        
        messages.success(request, 'Footer updated successfully!')
        return redirect('website_dashboard:footer_edit')
    
    context = {
        'footer': footer,
    }
    
    return render(request, 'myApp/website_dashboard/footer_edit.html', context)

