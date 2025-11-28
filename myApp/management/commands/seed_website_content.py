"""
Management command to seed initial website content
Run: python manage.py seed_website_content
"""
from django.core.management.base import BaseCommand
from myApp.models import (
    SEO, WebsiteHero, WebsiteSection, WebsiteTestimonial, WebsiteFooter
)


class Command(BaseCommand):
    help = 'Seed initial website content from database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seeding website content...'))
        
        # Create SEO
        seo, created = SEO.objects.get_or_create(
            pk=1,
            defaults={
                'page_title': 'KaTek AI - All-in-One AI CRM & Growth Engine',
                'meta_description': 'Transform your business with KaTek AI - the complete CRM and growth platform that connects everything.',
                'meta_keywords': 'AI CRM, marketing automation, business growth, customer management',
                'og_title': 'KaTek AI - All-in-One AI CRM & Growth Engine',
                'og_description': 'Turn every click, call, and comment into revenue with KaTek AI.',
                'twitter_card': 'summary_large_image',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created SEO settings'))
        else:
            self.stdout.write(self.style.WARNING('  SEO settings already exist'))
        
        # Create Hero
        hero, created = WebsiteHero.objects.get_or_create(
            pk=1,
            defaults={
                'pill_label': 'ALL-IN-ONE AI CRM',
                'main_headline': 'Turn Every Click, Call, and Comment Into Revenue',
                'subheadline': 'KaTek AI connects your CRM, campaigns, websites, bots, and reputation into one intelligent system that never sleeps.',
                'primary_cta_text': 'Schedule Your Call',
                'primary_cta_link': '#contact',
                'secondary_cta_text': 'See How It Works',
                'secondary_cta_link': '#platform',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Hero section'))
        else:
            self.stdout.write(self.style.WARNING('  Hero section already exists'))
        
        # Create Website Sections
        sections_data = [
            {
                'section_type': 'story',
                'title': 'The Journey',
                'subtitle': 'How we built KaTek AI',
                'description': 'From idea to reality',
                'is_active': True,
                'sort_order': 1,
            },
            {
                'section_type': 'platform',
                'title': 'Katalyst AI CRM',
                'subtitle': 'Your complete business command center',
                'description': 'All your tools in one place',
                'is_active': True,
                'sort_order': 2,
            },
            {
                'section_type': 'outcomes',
                'title': 'Real Results',
                'subtitle': 'See what our clients achieve',
                'description': 'Measurable outcomes',
                'is_active': True,
                'sort_order': 3,
            },
            {
                'section_type': 'ai_sales',
                'title': 'AI Sales & Customer Service',
                'subtitle': 'Automated follow-up and support',
                'description': 'Never miss a lead',
                'is_active': True,
                'sort_order': 4,
            },
            {
                'section_type': 'campaign_manager',
                'title': 'Campaign Manager',
                'subtitle': 'Multi-channel marketing campaigns',
                'description': 'Email, SMS, and more',
                'is_active': True,
                'sort_order': 5,
            },
            {
                'section_type': 'geo_distribution',
                'title': 'GEO & Distribution',
                'subtitle': 'Location-aware campaigns',
                'description': 'Target by location',
                'is_active': True,
                'sort_order': 6,
            },
            {
                'section_type': 'reputation',
                'title': 'Reputation Management',
                'subtitle': 'Monitor and improve your online reputation',
                'description': 'Stay on top of reviews',
                'is_active': True,
                'sort_order': 7,
            },
            {
                'section_type': 'ai_websites',
                'title': 'AI Websites',
                'subtitle': 'AI-generated websites and landing pages',
                'description': 'Built for conversion',
                'is_active': True,
                'sort_order': 8,
            },
            {
                'section_type': 'personas',
                'title': 'Who Is This For',
                'subtitle': 'Built for owners who are done with juggling 17 different tools',
                'description': 'Perfect for service businesses, SMB founders, and affiliate-driven brands',
                'is_active': True,
                'sort_order': 9,
            },
            {
                'section_type': 'testimonials',
                'title': 'The Proof Is In The Pipeline',
                'subtitle': "We've helped 100s of coaches and entrepreneurs build automated marketing systems",
                'description': 'See what our clients say',
                'is_active': True,
                'sort_order': 10,
            },
            {
                'section_type': 'final_cta',
                'title': 'Ready to see your business on autopilot?',
                'subtitle': "Book a live walkthrough and we'll map Katalyst AI to your exact workflows",
                'description': 'Get started today',
                'is_active': True,
                'sort_order': 11,
            },
        ]
        
        for section_data in sections_data:
            section, created = WebsiteSection.objects.get_or_create(
                section_type=section_data['section_type'],
                defaults=section_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Created {section_data['section_type']} section"))
            else:
                self.stdout.write(self.style.WARNING(f"  {section_data['section_type']} section already exists"))
        
        # Create Sample Testimonials
        testimonials_data = [
            {
                'quote': "If you ever have the opportunity and the good fortune to work with the team, consider yourself one of the luckiest people in the world!",
                'author_name': 'David Alemian',
                'author_title': 'Business Consultant',
                'sort_order': 1,
                'is_active': True,
            },
            {
                'quote': "The Katalyst CRM team set my CRM up and created my webinar landing page in 48 hours!",
                'author_name': 'Edoardo Costa',
                'author_title': 'Actor, Author & Mindset Breakthrough Mentor',
                'sort_order': 2,
                'is_active': True,
            },
            {
                'quote': "The team totally got my brand and message and designed my landing page and funnel in 3 days",
                'author_name': 'Andy Gupta',
                'author_title': 'Ex-Goldman Sachs, Private Equity Investor',
                'sort_order': 3,
                'is_active': True,
            },
            {
                'quote': "Working with the team behind is like sailing on a smooth ocean with a gentle breeze!",
                'author_name': 'Rita Esterly',
                'author_title': 'Business Consultant',
                'sort_order': 4,
                'is_active': True,
            },
            {
                'quote': "When it came to landing pages, websites, and anything tech, Katalyst made it possible",
                'author_name': 'Coralsz',
                'author_title': 'Co-founder of the Speak Up and Lead Academy',
                'sort_order': 5,
                'is_active': True,
            },
        ]
        
        for testimonial_data in testimonials_data:
            testimonial, created = WebsiteTestimonial.objects.get_or_create(
                author_name=testimonial_data['author_name'],
                defaults=testimonial_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Created testimonial from {testimonial_data['author_name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"  Testimonial from {testimonial_data['author_name']} already exists"))
        
        # Create Footer
        footer, created = WebsiteFooter.objects.get_or_create(
            pk=1,
            defaults={
                'copyright_text': '© 2024 KaTek AI. All rights reserved.',
                'social_links': {},
                'footer_links': [],
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Footer'))
        else:
            self.stdout.write(self.style.WARNING('  Footer already exists'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Website content seeding completed!'))
        self.stdout.write(self.style.SUCCESS('You can now edit content in the Website Dashboard.'))

