"""
Content Helpers - Convert database models to template context
"""
from .models import (
    SEO, WebsiteHero, WebsiteSection, WebsiteTestimonial, WebsiteFooter
)


def get_website_content_from_db():
    """
    Get all website content from database and return as dictionary
    Falls back to None if content doesn't exist (templates will use defaults)
    """
    content = {}
    
    try:
        # SEO
        seo = SEO.objects.first()
        if seo:
            content['seo'] = {
                'page_title': seo.page_title,
                'meta_description': seo.meta_description,
                'meta_keywords': seo.meta_keywords,
                'og_title': seo.og_title,
                'og_description': seo.og_description,
                'og_image_url': seo.og_image_url,
                'twitter_card': seo.twitter_card,
                'canonical_url': seo.canonical_url,
            }
    except Exception:
        pass
    
    try:
        # Hero
        hero = WebsiteHero.objects.filter(is_active=True).first()
        if hero:
            content['hero'] = {
                'pill_label': hero.pill_label,
                'main_headline': hero.main_headline,
                'subheadline': hero.subheadline,
                'primary_cta_text': hero.primary_cta_text,
                'primary_cta_link': hero.primary_cta_link,
                'secondary_cta_text': hero.secondary_cta_text,
                'secondary_cta_link': hero.secondary_cta_link,
                'background_image_url': hero.background_image_url,
                'dashboard_image_url': hero.dashboard_image_url,
            }
    except Exception:
        pass
    
    try:
        # Sections
        sections = WebsiteSection.objects.filter(is_active=True).order_by('sort_order')
        content['sections'] = {}
        for section in sections:
            content['sections'][section.section_type] = {
                'title': section.title,
                'subtitle': section.subtitle,
                'description': section.description,
                'content': section.content,
                'background_image_url': section.background_image_url,
            }
    except Exception:
        pass
    
    try:
        # Testimonials
        testimonials = WebsiteTestimonial.objects.filter(is_active=True).order_by('sort_order', '-created_at')
        content['testimonials'] = [
            {
                'quote': t.quote,
                'author_name': t.author_name,
                'author_title': t.author_title,
                'avatar_url': t.avatar_url,
            }
            for t in testimonials
        ]
    except Exception:
        pass
    
    try:
        # Footer
        footer = WebsiteFooter.objects.first()
        if footer:
            content['footer'] = {
                'copyright_text': footer.copyright_text,
                'social_links': footer.social_links or {},
                'footer_links': footer.footer_links or [],
            }
    except Exception:
        pass
    
    return content

