# KaTek AI Main Page - Design Documentation

## Overview
This document describes the current design, structure, and styling of the main landing page (`home.html`). Use this as a reference when redesigning or adding background images and other visual elements.

---

## Page Structure & Layout

### File Organization
- **Main Template**: `myApp/templates/myApp/home.html`
- **Base Template**: `myApp/templates/myApp/base.html`
- **Partials Directory**: `myApp/templates/myApp/partials/`

### Page Sections (Top to Bottom)
1. **Header** (`partials/header.html`) - Fixed/sticky navigation
2. **Hero Section** (`partials/hero.html`) - Main landing area
3. **Story Section** (`partials/story.html`) - "How It Works" flow
4. **Platform Section** (`partials/platform.html`) - CRM features
5. **AI Sales & Customer Service** (`partials/ai_sales.html`)
6. **Campaign Manager** (`partials/campaign_manager.html`)
7. **GEO & Distribution** (`partials/geo_distribution.html`)
8. **Reputation** (`partials/reputation.html`)
9. **AI Websites** (`partials/ai_websites.html`)
10. **Personas** (`partials/personas.html`)
11. **Results** (`partials/results.html`) - Stats and testimonials
12. **Final CTA** (`partials/final_cta.html`) - Call-to-action
13. **Footer** (`partials/footer.html`)

---

## Design System

### Color Palette

#### Primary Colors (Gradient Accents)
- **Cyan**: `#06b6d4` (cyan-500), `#22d3ee` (cyan-400), `#0891b2` (cyan-600)
- **Violet**: `#8b5cf6` (violet-500), `#a78bfa` (violet-400), `#7c3aed` (violet-600)
- **Pink**: `#ec4899` (pink-500), `#f472b6` (pink-400), `#db2777` (pink-600)

#### Background Colors (Dark Mode - Default)
- **Main Background**: `#020617` (slate-950)
- **Card Backgrounds**: `#0f172a` (slate-900) with opacity variations
- **Secondary Backgrounds**: `#1e293b` (slate-800)
- **Borders**: `#334155` (slate-700) with opacity variations

#### Background Colors (Light Mode)
- **Main Background**: `#f8fafc` (light gray)
- **Card Backgrounds**: `#ffffff` (white) with opacity variations
- **Secondary Backgrounds**: `#f1f5f9` (light slate)
- **Borders**: `#cbd5e1` (light slate border)

#### Text Colors
- **Primary Text (Dark)**: `#f1f5f9` (slate-100)
- **Secondary Text (Dark)**: `#cbd5e1` (slate-300), `#94a3b8` (slate-400)
- **Primary Text (Light)**: `#0f172a` (dark slate)
- **Secondary Text (Light)**: `#334155` (slate-700), `#475569` (slate-600)

### Typography

#### Font Families
- **Body Text**: `Inter` (Google Fonts)
  - Weights: 300, 400, 500, 600, 700, 800, 900
- **Headings**: `Poppins` (Google Fonts)
  - Weights: 300, 400, 500, 600, 700, 800, 900

#### Font Sizes
- **Hero Headline**: `text-4xl md:text-5xl lg:text-6xl` (2.25rem - 3.75rem)
- **Section Headings**: `text-3xl md:text-4xl lg:text-5xl` (1.875rem - 3rem)
- **Subheadings**: `text-xl md:text-2xl` (1.25rem - 1.5rem)
- **Body Text**: `text-base md:text-lg` (1rem - 1.125rem)
- **Small Text**: `text-sm` (0.875rem)

### Spacing & Layout
- **Max Container Width**: `max-w-7xl` (80rem / 1280px)
- **Section Padding**: `py-16 md:py-24` (vertical), `px-6 md:px-10` (horizontal)
- **Card Padding**: `p-6 md:p-8`
- **Gap Between Elements**: `gap-4`, `gap-6`, `gap-8`, `gap-12`

---

## Current Background & Visual Elements

### Background Images
**Currently: NO background images are used.** The page uses:
- Solid color backgrounds (`bg-slate-950` for dark mode, `bg-slate-50` for light mode)
- Gradient overlays on specific sections (e.g., `bg-gradient-to-r from-cyan-500/20 via-violet-500/20 to-pink-500/20`)
- Glassmorphism effects with backdrop blur (`backdrop-blur-md`)

### Visual Effects Currently Used
1. **Glassmorphism**: 
   - Header: `bg-slate-950/70 backdrop-blur-md`
   - Cards: `bg-slate-900/80` or `bg-slate-900/90`

2. **Gradients**:
   - Buttons: `bg-gradient-to-r from-cyan-500 to-violet-500`
   - Section backgrounds: `bg-gradient-to-r from-cyan-500/20 via-violet-500/20 to-pink-500/20`
   - Text gradients: `bg-gradient-to-r from-cyan-400 to-violet-400` with `text-transparent bg-clip-text`

3. **Shadows**:
   - Cards: `shadow-xl`, `shadow-2xl`
   - Hover effects: `hover:shadow-[0_0_30px_rgba(56,189,248,0.5)]`
   - Glowing borders: `shadow-[0_0_25px_rgba(56,189,248,0.35)]`

4. **Borders**:
   - Standard: `border border-slate-700/70`
   - Gradient borders: `bg-gradient-to-r from-pink-500/40 via-violet-500/40 to-cyan-400/40 p-[1px]`

---

## Component Details

### 1. Header (Sticky Navigation)
**File**: `partials/header.html`

**Structure**:
- Fixed position at top (`fixed top-0`)
- Semi-transparent background with blur
- Logo (gradient icon + text)
- Navigation links (hidden on mobile)
- Theme toggle button
- CTA button

**Current Styling**:
- Background: `bg-slate-950/70 backdrop-blur-md`
- Border: `border-b border-slate-800/50`
- Height: `py-4` (padding)

**Where to Add Background Image**:
- Could add a background image to the entire header or just behind the logo area
- Consider overlay opacity to maintain readability

---

### 2. Hero Section
**File**: `partials/hero.html`

**Structure**:
- Two-column layout (content left, visual card right)
- Headline with gradient text
- Value points with icons
- CTA buttons
- Command center card mockup on right

**Current Styling**:
- Full viewport height: `min-h-screen`
- Padding top: `pt-28 md:pt-36` (accounts for fixed header)
- Background: Inherits from body (`bg-slate-950`)

**Where to Add Background Image**:
- **Option 1**: Full section background (behind all content)
- **Option 2**: Background behind the command center card
- **Option 3**: Subtle pattern/texture overlay
- **Option 4**: Animated gradient mesh or particles

**Visual Card Elements**:
- Command center mockup with gradient borders
- Floating stat bubbles (absolute positioned)
- Chart visualization (bar chart mockup)

---

### 3. Story Section ("How It Works")
**File**: `partials/story.html`

**Structure**:
- Vertical timeline with connecting line
- 6 steps with icons and descriptions
- Color-coded icons (cyan, violet, pink, yellow, green)

**Current Styling**:
- Background: `bg-slate-950`
- Vertical line: `bg-gradient-to-b from-cyan-500/50 via-violet-500/50 to-pink-500/50`
- Icon circles: `bg-slate-900 border-2` with colored borders

**Where to Add Background Image**:
- Could add a subtle pattern or texture
- Consider diagonal lines or geometric shapes
- Background could be behind the timeline line

---

### 4. Platform Section
**File**: `partials/platform.html`

**Structure**:
- Two-column layout (screenshot mockup left, title right)
- Feature grid (4 cards)
- Large analytics card at bottom

**Current Styling**:
- Background: `bg-slate-950`
- Cards: `bg-slate-900/80 border border-slate-700/70`
- Hover effects: `hover:border-cyan-400 hover:shadow-[0_0_30px_rgba(34,211,238,0.4)]`

**Where to Add Background Image**:
- Could add a dashboard/screenshot background
- Pattern overlay for texture
- Subtle grid or mesh pattern

---

### 5. AI Sales & Customer Service
**File**: `partials/ai_sales.html`

**Structure**:
- Two-column feature cards (top row)
- Two smaller cards (bottom row)
- Icons with colored accents

**Current Styling**:
- Background: `bg-slate-950`
- Cards: `bg-slate-900/80 border border-slate-700/70`

**Where to Add Background Image**:
- Communication-themed imagery (chat bubbles, phone icons)
- Abstract tech patterns

---

### 6. Campaign Manager
**File**: `partials/campaign_manager.html`

**Structure**:
- Three stacked cards with gradient borders
- Each card has icon, title, and description

**Current Styling**:
- Background: `bg-slate-950`
- Cards: Gradient border wrapper with `bg-slate-900/90` inner
- Gradient: `bg-gradient-to-r from-pink-500/40 via-violet-500/40 to-cyan-400/40`

**Where to Add Background Image**:
- Marketing/campaign themed imagery
- Chart/graph patterns
- Abstract data visualization backgrounds

---

### 7. Results Section
**File**: `partials/results.html`

**Structure**:
- Three stat cards with large numbers
- Testimonial card

**Current Styling**:
- Background: `bg-slate-950`
- Stat numbers: Gradient text (`bg-gradient-to-r from-cyan-400 to-violet-400`)
- Cards: `bg-slate-900/80 border border-slate-700/70`

**Where to Add Background Image**:
- Success/growth imagery
- Abstract celebration patterns
- Subtle confetti or success symbols

---

### 8. Final CTA Section
**File**: `partials/final_cta.html`

**Structure**:
- Centered card with heading, description, buttons
- Trust indicators at bottom

**Current Styling**:
- Background: `bg-gradient-to-r from-cyan-500/20 via-violet-500/20 to-pink-500/20`
- Card: `bg-slate-900/90 border border-slate-700/70`

**Where to Add Background Image**:
- **High priority**: This section would benefit from a compelling background image
- Could use abstract tech imagery, business growth visuals, or branded imagery
- Consider overlay to maintain text readability

---

### 9. Footer
**File**: `partials/footer.html`

**Structure**:
- 4-column grid (logo, product links, resources, contact)
- Social media icons
- Copyright text

**Current Styling**:
- Background: `bg-slate-950`
- Border top: `border-t border-slate-800`

**Where to Add Background Image**:
- Subtle pattern or texture
- Dark abstract design
- Branded footer background

---

## Theme System (Dark/Light Mode)

### Implementation
- Toggle button in header
- Theme stored in `localStorage`
- CSS classes: `html.light-mode` for light mode
- All colors have light mode overrides in `base.html`

### Current Behavior
- **Default**: Dark mode
- **Toggle**: Moon icon (dark) / Sun icon (light)
- **Persistence**: Saved in browser localStorage

### Background Image Considerations for Themes
- If adding background images, consider:
  - Different images for dark vs light mode
  - Overlay opacity adjustments per theme
  - Image brightness/contrast adjustments

---

## Responsive Design

### Breakpoints (Tailwind CSS)
- **Mobile**: Default (< 640px)
- **Tablet**: `md:` (≥ 768px)
- **Desktop**: `lg:` (≥ 1024px)
- **Large Desktop**: `xl:` (≥ 1280px)

### Current Responsive Features
- Navigation: Hidden on mobile, visible on desktop
- Grid layouts: 1 column mobile, 2+ columns desktop
- Typography: Scales down on mobile
- Padding: Smaller on mobile, larger on desktop
- Hero section: Stacks vertically on mobile

### Background Image Responsive Considerations
- Use `background-size: cover` or `contain` as needed
- Consider different images for mobile vs desktop
- Ensure images don't slow down mobile loading
- Use `srcset` or responsive image techniques

---

## Current CSS Framework & Tools

### Framework
- **Tailwind CSS** (via CDN): `https://cdn.tailwindcss.com`
- **Font Awesome** (Icons): `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css`
- **Google Fonts**: Inter & Poppins

### Custom Styles
- Located in `<style>` tag in `base.html`
- Light mode overrides
- Font family assignments
- Theme-specific color adjustments

---

## How to Add Background Images

### Method 1: Section-Level Backgrounds
Add to individual section elements:
```html
<section class="py-16 md:py-24 px-6 md:px-10 bg-slate-950 relative">
    <!-- Background Image -->
    <div class="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-10" 
         style="background-image: url('path/to/image.jpg'); z-index: 0;"></div>
    <!-- Content -->
    <div class="relative z-10">
        <!-- Section content -->
    </div>
</section>
```

### Method 2: Body/Base Background
Add to `base.html` body element:
```html
<body class="bg-slate-950 text-slate-100 antialiased transition-colors duration-300"
      style="background-image: url('path/to/image.jpg'); background-size: cover; background-position: center; background-attachment: fixed;">
```

### Method 3: CSS Background Classes
Add custom classes in `base.html`:
```css
.bg-hero-pattern {
    background-image: url('path/to/image.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}
```

### Method 4: Inline Styles in Partials
Add directly to section elements in partial files:
```html
<section style="background-image: url('path/to/image.jpg'); background-size: cover;">
```

### Recommended Approach
1. **Create a static images directory**: `myApp/static/myApp/images/`
2. **Use Django static files**: `{% load static %}` and `{% static 'myApp/images/bg.jpg' %}`
3. **Add overlay divs** for opacity control
4. **Test with both dark and light themes**
5. **Optimize images** (WebP format, compressed)

---

## Key Design Patterns

### Cards
- Rounded corners: `rounded-2xl` or `rounded-3xl`
- Borders: `border border-slate-700/70`
- Backgrounds: `bg-slate-900/80` or `bg-slate-900/90`
- Shadows: `shadow-xl` or `shadow-2xl`
- Hover effects: Border color change, shadow glow

### Buttons
- Primary: `bg-gradient-to-r from-cyan-500 to-violet-500`
- Secondary: `border border-slate-700` with hover effects
- Hover: `hover:shadow-[0_0_40px_rgba(56,189,248,0.5)]` and `hover:-translate-y-1`

### Icons
- Font Awesome icons
- Colored with accent colors (cyan, violet, pink, yellow, green)
- Sizes: `text-lg`, `text-xl`, `text-2xl`

### Gradients
- Text gradients: `text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-400`
- Background gradients: `bg-gradient-to-r from-cyan-500/20 via-violet-500/20 to-pink-500/20`
- Border gradients: Wrapper div with gradient background and inner div

---

## Animation & Interactions

### Current Animations
- Smooth scroll: JavaScript for anchor links
- Hover transitions: `transition-all duration-300`
- Theme toggle: Instant (no animation)
- Card hover: Scale, border color, shadow glow

### Potential Enhancements
- Scroll-triggered animations (fade-in, slide-up)
- Parallax effects for background images
- Animated gradients
- Particle effects
- Loading animations

---

## Performance Considerations

### Current Optimizations
- Tailwind CSS via CDN (no build step)
- Font Awesome via CDN
- Google Fonts with preconnect

### When Adding Background Images
- **Optimize images**: Compress, use WebP format
- **Lazy loading**: Use `loading="lazy"` for images
- **Responsive images**: Different sizes for different breakpoints
- **CDN**: Consider hosting images on a CDN
- **CSS sprites**: For small repeating patterns

---

## Accessibility Notes

### Current Features
- Semantic HTML structure
- ARIA labels on theme toggle button
- Color contrast (tested for dark/light modes)

### When Adding Background Images
- Ensure text remains readable (sufficient contrast)
- Don't rely solely on color for information
- Test with screen readers
- Maintain focus indicators
- Consider reduced motion preferences

---

## File Locations Reference

```
myProject/
├── myApp/
│   ├── templates/
│   │   └── myApp/
│   │       ├── base.html          # Base template with styles
│   │       ├── home.html          # Main page (includes partials)
│   │       └── partials/
│   │           ├── header.html
│   │           ├── hero.html
│   │           ├── story.html
│   │           ├── platform.html
│   │           ├── ai_sales.html
│   │           ├── campaign_manager.html
│   │           ├── geo_distribution.html
│   │           ├── reputation.html
│   │           ├── ai_websites.html
│   │           ├── personas.html
│   │           ├── results.html
│   │           ├── final_cta.html
│   │           └── footer.html
│   └── static/
│       └── myApp/
│           └── images/            # Create this for background images
```

---

## Quick Reference: Color Codes

### Dark Mode
- Background: `#020617` (slate-950)
- Cards: `#0f172a` (slate-900)
- Borders: `#334155` (slate-700)
- Text Primary: `#f1f5f9` (slate-100)
- Text Secondary: `#cbd5e1` (slate-300)

### Light Mode
- Background: `#f8fafc` (slate-50)
- Cards: `#ffffff` (white)
- Borders: `#cbd5e1` (slate-300)
- Text Primary: `#0f172a` (slate-900)
- Text Secondary: `#334155` (slate-700)

### Accent Colors
- Cyan: `#06b6d4` / `#22d3ee`
- Violet: `#8b5cf6` / `#a78bfa`
- Pink: `#ec4899` / `#f472b6`

---

## Next Steps for Redesign

1. **Decide on background image strategy**:
   - Full page background?
   - Section-specific backgrounds?
   - Pattern overlays?
   - Animated backgrounds?

2. **Create image assets**:
   - Optimize for web
   - Create different sizes for responsive design
   - Consider dark/light mode variations

3. **Update partial files**:
   - Add background image divs
   - Adjust opacity and overlays
   - Test readability

4. **Test across devices**:
   - Mobile, tablet, desktop
   - Different screen sizes
   - Both themes (dark/light)

5. **Performance testing**:
   - Image loading times
   - Page speed
   - Mobile performance

---

**Last Updated**: Based on current codebase structure
**Document Version**: 1.0

