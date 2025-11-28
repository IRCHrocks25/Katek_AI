# Image Placeholders Guide

This document lists all the placeholder images that need to be replaced with actual assets.

## Image Directory Structure

All images should be placed in: `myApp/static/myApp/images/`

## Required Images

### 1. Hero Section
- **File**: `hero-background.jpg`
- **Location**: Hero section background (behind neon waves)
- **Recommended Size**: 1920x1080px or larger
- **Description**: Dark, abstract background with neon wave-like patterns or gradients

- **File**: `hero-dashboard.jpg`
- **Location**: Dashboard mockup card in hero section
- **Recommended Size**: 1200x800px or larger
- **Description**: Screenshot of the KaTek AI dashboard showing stats, charts, and metrics

### 2. AI Websites Section
- **File**: `website-mockup.jpg`
- **Location**: Top-left card in AI websites section
- **Recommended Size**: 800x600px
- **Description**: Screenshot of an AI-generated website

- **File**: `landing-page-preview.jpg`
- **Location**: Top-right card in AI websites section
- **Recommended Size**: 400x600px (vertical/portrait orientation)
- **Description**: Mobile or desktop preview of a landing page

### 3. Reputation Section
- **File**: `reputation-chart.jpg`
- **Location**: Analytics card in reputation section
- **Recommended Size**: 600x200px
- **Description**: Line chart or graph showing reputation metrics/trends

### 4. Testimonials Section
- **File**: `testimonial-1.jpg`
- **Location**: First testimonial card (Sarah M.)
- **Recommended Size**: 128x128px (square, will be displayed as circle)
- **Description**: Profile photo of testimonial author

- **File**: `testimonial-2.jpg`
- **Location**: Second testimonial card (James R.)
- **Recommended Size**: 128x128px (square, will be displayed as circle)
- **Description**: Profile photo of testimonial author

- **File**: `testimonial-3.jpg`
- **Location**: Third testimonial card (Maria L.)
- **Recommended Size**: 128x128px (square, will be displayed as circle)
- **Description**: Profile photo of testimonial author

- **File**: `testimonial-4.jpg`
- **Location**: Fourth testimonial card (David K.)
- **Recommended Size**: 128x128px (square, will be displayed as circle)
- **Description**: Profile photo of testimonial author

## Image Format Recommendations

- **Format**: JPG or PNG (JPG for photos, PNG for graphics with transparency)
- **Optimization**: Compress images for web (use tools like TinyPNG, ImageOptim, or similar)
- **Naming**: Use lowercase with hyphens (kebab-case) as shown above

## Fallback Behavior

All images have fallback displays that will show if the image file is missing:
- Hero dashboard: Shows a styled mockup with stats and charts
- Website/landing page mockups: Shows placeholder rectangles
- Reputation chart: Shows gradient bar chart
- Testimonial photos: Shows a user icon

## How to Add Images

1. Create the directory if it doesn't exist: `myApp/static/myApp/images/`
2. Place your image files in that directory with the exact filenames listed above
3. Run `python manage.py collectstatic` if using Django's static files in production
4. The images will automatically load when the page is viewed

## Notes

- All images use Django's `{% static %}` tag for proper path resolution
- Images are set to gracefully degrade if missing (fallback displays)
- Make sure to optimize images for web to maintain fast page load times
- Consider using WebP format for better compression (requires additional setup)

