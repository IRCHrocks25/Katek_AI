"""
Website Dashboard URLs
"""
from django.urls import path
from . import website_dashboard_views

app_name = 'website_dashboard'

urlpatterns = [
    # Dashboard Home
    path('', website_dashboard_views.website_dashboard_home, name='home'),
    
    # Image Management
    path('gallery/', website_dashboard_views.website_gallery, name='gallery'),
    path('gallery/api/', website_dashboard_views.website_gallery_api, name='gallery_api'),
    path('upload-image/', website_dashboard_views.website_upload_image, name='upload_image'),
    
    # Content Management
    path('seo/', website_dashboard_views.website_seo_edit, name='seo_edit'),
    path('hero/', website_dashboard_views.website_hero_edit, name='hero_edit'),
    path('section/<str:section_type>/', website_dashboard_views.website_section_edit, name='section_edit'),
    path('testimonials/', website_dashboard_views.website_testimonials_list, name='testimonials_list'),
    path('testimonials/new/', website_dashboard_views.website_testimonial_edit, name='testimonial_new'),
    path('testimonials/<int:testimonial_id>/edit/', website_dashboard_views.website_testimonial_edit, name='testimonial_edit'),
    path('testimonials/<int:testimonial_id>/delete/', website_dashboard_views.website_testimonial_delete, name='testimonial_delete'),
    path('footer/', website_dashboard_views.website_footer_edit, name='footer_edit'),
]

