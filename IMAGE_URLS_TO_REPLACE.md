# Image URLs to Replace

All placeholder images are now using external URLs. Replace these URLs with your actual image URLs.

## Hero Section

### Background Image
- **Current URL**: `https://images.unsplash.com/photo-1557683316-973673baf926?w=1920&h=1080&fit=crop`
- **Location**: Hero section background (behind neon waves, opacity 20%)
- **File**: `myApp/templates/myApp/partials/hero.html` (line ~6)
- **Replace with**: Your hero background image URL

### Dashboard Mockup
- **Current URL**: `https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&h=800&fit=crop`
- **Location**: Dashboard card in hero section
- **File**: `myApp/templates/myApp/partials/hero.html` (line ~40)
- **Replace with**: Your dashboard screenshot URL

## AI Websites Section

### Overlapping Website Screenshots
- **Current URL**: `https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=800&h=600&fit=crop`
- **Location**: Right side of top "AI-generated websites" card
- **File**: `myApp/templates/myApp/partials/ai_websites.html` (line ~30)
- **Replace with**: Your overlapping website screenshots image URL (showing multiple website examples like VR site, travel site, etc.)
- **Note**: This should show 3-4 overlapping/angled website screenshots

## Outcomes Section

### Background Image
- **Current URL**: `https://images.unsplash.com/photo-1557683316-973673baf926?w=1920&h=1080&fit=crop`
- **Location**: Full section background (behind glassmorphism cards)
- **File**: `myApp/templates/myApp/partials/outcomes.html` (line ~6)
- **Replace with**: Your outcomes background image URL (dark blue with abstract glowing lines)
- **Note**: Image has 30% opacity to allow background effects to show through

## GEO Distribution Section

### Left Side Background Image
- **Current URL**: `https://images.unsplash.com/photo-1557683316-973673baf926?w=1920&h=1080&fit=crop`
- **Location**: Left column background (behind text content)
- **File**: `myApp/templates/myApp/partials/geo_distribution.html` (line ~8)
- **Replace with**: Your background image URL (dark blue with glowing blue/white abstract lines)
- **Note**: Image has 40% opacity with neon wave overlay for glowing effect

## Reputation Section

### Dashboard UI Image
- **Current URL**: `https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=1000&fit=crop`
- **Location**: Right column - full dashboard UI screenshot
- **File**: `myApp/templates/myApp/partials/reputation.html` (line ~60)
- **Replace with**: Your dashboard UI screenshot URL (showing the three UI modules: Online Reputation Manager, Feedback Analysis, and Corrective Messaging Module)
- **Note**: This should be a single image showing all three dashboard modules stacked vertically

## Personas Section (Who Is This For)

### Background Image
- **Current URL**: `https://images.unsplash.com/photo-1557683316-973673baf926?w=1920&h=1080&fit=crop`
- **Location**: Full section background (behind glassmorphism cards and neon waves)
- **File**: `myApp/templates/myApp/partials/personas.html` (line ~6)
- **Replace with**: Your personas background image URL (dark blue with abstract glowing blue and green light streaks)
- **Note**: Image has 30% opacity to allow neon wave effects to show through

## Testimonials Section

### Profile Photos
- **Current URLs**: Using `https://i.pravatar.cc/128?img=X` (different numbers for each)
- **Location**: Testimonial cards
- **File**: `myApp/templates/myApp/partials/testimonials.html`
- **Replace with**: Your testimonial profile photo URLs

## Final CTA Section

### Background Image
- **Current URL**: `https://images.unsplash.com/photo-1557683316-973673baf926?w=1920&h=1080&fit=crop`
- **Location**: Full section background (behind neon waves and content)
- **File**: `myApp/templates/myApp/partials/final_cta.html` (line ~6)
- **Replace with**: Your final CTA background image URL (dark navy blue with abstract glowing blue and teal light streaks)
- **Note**: Image has 20% opacity to allow neon wave effects and halo glow to show through

## How to Replace

1. Open the template file listed above
2. Find the `<img src="...">` tag with the placeholder URL
3. Replace the URL with your actual image URL
4. Save the file

## Notes

- All images have fallback displays if the URL fails to load
- Images are set to `object-cover` for proper scaling
- Hero background has `opacity-20` class for subtle overlay effect
- Dashboard image is full width with rounded corners
- Testimonial photos are circular (128x128px)

