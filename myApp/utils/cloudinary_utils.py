"""
Cloudinary utilities for image upload and optimization
"""
import io
from PIL import Image
import cloudinary
import cloudinary.uploader
from django.conf import settings
import os

# Compression settings
MAX_BYTES = 10 * 1024 * 1024  # 10MB
TARGET_BYTES = int(MAX_BYTES * 0.93)  # 9.3MB target


def smart_compress_to_bytes(image_file, target_bytes=TARGET_BYTES, max_quality=95, min_quality=60):
    """
    Compress an image to target size while maintaining quality.
    Uses progressive quality reduction if needed.
    """
    try:
        # Open image
        img = Image.open(image_file)
        
        # Convert RGBA to RGB if needed (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # Get original size
        original_size = len(image_file.read()) if hasattr(image_file, 'read') else 0
        image_file.seek(0) if hasattr(image_file, 'seek') else None
        
        # If already small enough, return as-is
        if original_size <= target_bytes:
            image_file.seek(0) if hasattr(image_file, 'seek') else None
            return image_file.read() if hasattr(image_file, 'read') else image_file
        
        # Try different quality levels
        quality = max_quality
        output = io.BytesIO()
        
        while quality >= min_quality:
            output.seek(0)
            output.truncate(0)
            
            # Save with current quality
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            # Check size
            size = output.tell()
            if size <= target_bytes:
                output.seek(0)
                return output.read()
            
            # Reduce quality for next iteration
            quality -= 5
        
        # If still too large, try resizing
        if output.tell() > target_bytes:
            # Calculate resize factor
            current_size = output.tell()
            resize_factor = (target_bytes / current_size) ** 0.5
            new_width = int(img.width * resize_factor)
            new_height = int(img.height * resize_factor)
            
            # Resize image
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save resized image
            output.seek(0)
            output.truncate(0)
            img_resized.save(output, format='JPEG', quality=min_quality, optimize=True)
            output.seek(0)
            return output.read()
        
        # Fallback: return what we have
        output.seek(0)
        return output.read()
    
    except Exception as e:
        # If compression fails, return original
        print(f"Compression error: {e}")
        if hasattr(image_file, 'seek'):
            image_file.seek(0)
        if hasattr(image_file, 'read'):
            return image_file.read()
        return image_file


def upload_to_cloudinary(image_file, folder='katek_ai/uploads', public_id=None, resource_type='image'):
    """
    Upload image to Cloudinary with smart compression and optimization.
    
    Returns:
        dict with keys: url, secure_url, public_id, width, height, format, bytes
    """
    try:
        # Compress image before upload
        compressed_data = smart_compress_to_bytes(image_file)
        
        # Create file-like object from compressed data
        compressed_file = io.BytesIO(compressed_data)
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            compressed_file,
            folder=folder,
            public_id=public_id,
            resource_type=resource_type,
            overwrite=True,
            invalidate=True,
            transformation=[
                {'quality': 'auto', 'fetch_format': 'auto'}
            ]
        )
        
        # Generate URL variants
        secure_url = upload_result.get('secure_url', '')
        public_id = upload_result.get('public_id', '')
        
        # Web-optimized URL
        web_url = secure_url.replace('/upload/', '/upload/f_webp,q_80,w_1920/')
        
        # Thumbnail URL
        thumbnail_url = secure_url.replace('/upload/', '/upload/f_webp,q_70,w_400,h_400,c_fill/')
        
        return {
            'url': upload_result.get('url', ''),
            'secure_url': secure_url,
            'public_id': public_id,
            'web_url': web_url,
            'thumbnail_url': thumbnail_url,
            'width': upload_result.get('width', 0),
            'height': upload_result.get('height', 0),
            'format': upload_result.get('format', ''),
            'bytes': upload_result.get('bytes', 0),
            'original_url': secure_url,  # Keep original for reference
        }
    
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        raise Exception(f"Failed to upload image: {str(e)}")

