#!/usr/bin/env python3
"""
Generate stock banner images and square images for topics/causes using Google Gemini.

This script creates professional banner images (1200x600) and square images (400x400)
for trending topics and causes to use on the homepage and throughout the site.

Usage:
    python scripts/media/generate_topic_images.py --topic "World Press Freedom Day"
    python scripts/media/generate_topic_images.py --topic "Artificial Intelligence" --output-dir data/media/topics
    python scripts/media/generate_topic_images.py --batch --topics-file topics.txt
"""

import os
import sys
import argparse
import base64
from pathlib import Path
from typing import Optional, List
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    from PIL import Image, ImageDraw, ImageFont
    import requests
    from io import BytesIO
except ImportError:
    print("❌ Missing required packages. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "google-generativeai", "pillow", "requests", "python-dotenv"])
    import google.generativeai as genai
    from PIL import Image, ImageDraw, ImageFont
    import requests
    from io import BytesIO


class TopicImageGenerator:
    """Generate professional banner and square images for topics using Gemini."""
    
    def __init__(self, api_key: Optional[str] = None, output_dir: str = "data/media/topics"):
        """Initialize the generator.
        
        Args:
            api_key: Google Gemini API key (defaults to GEMINI_API_KEY env var)
            output_dir: Directory to save generated images
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables or .env file")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use Gemini Pro for text generation (image generation coming soon)
        # For now, we'll generate placeholder images with professional styling
        self.model = genai.GenerativeModel('gemini-pro')
        
        print(f"✅ Initialized TopicImageGenerator")
        print(f"📁 Output directory: {self.output_dir}")
    
    def generate_color_scheme(self, topic: str) -> dict:
        """Use Gemini to suggest a color scheme for the topic.
        
        Args:
            topic: The topic name
            
        Returns:
            Dictionary with primary, secondary, and text colors
        """
        prompt = f"""For the topic "{topic}", suggest a professional color scheme suitable for news/media.
        
        Respond in JSON format with these fields:
        {{
            "primary": "#HEXCODE",
            "secondary": "#HEXCODE", 
            "text": "#HEXCODE",
            "background": "#HEXCODE",
            "reasoning": "brief explanation"
        }}
        
        Consider:
        - Professional, trustworthy colors
        - Good contrast and readability
        - Thematic relevance to the topic
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            text = response.text.strip()
            # Remove markdown code blocks if present
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            
            colors = json.loads(text.strip())
            print(f"🎨 Generated color scheme: {colors['reasoning']}")
            return colors
        except Exception as e:
            print(f"⚠️ Failed to generate color scheme: {e}")
            # Default professional scheme
            return {
                "primary": "#2563EB",
                "secondary": "#7C3AED",
                "text": "#FFFFFF",
                "background": "#1E293B",
                "reasoning": "Default professional blue scheme"
            }
    
    def create_banner_image(self, topic: str, colors: dict, size: tuple = (1200, 600)) -> Image.Image:
        """Create a professional banner image.
        
        Args:
            topic: Topic name
            colors: Color scheme dictionary
            size: Image size (width, height)
            
        Returns:
            PIL Image object
        """
        # Create image
        img = Image.new('RGB', size, colors['background'])
        draw = ImageDraw.Draw(img)
        
        # Add gradient effect
        for i in range(size[1]):
            alpha = i / size[1]
            # Interpolate between primary and secondary
            r1, g1, b1 = tuple(int(colors['primary'][j:j+2], 16) for j in (1, 3, 5))
            r2, g2, b2 = tuple(int(colors['secondary'][j:j+2], 16) for j in (1, 3, 5))
            r = int(r1 * (1 - alpha) + r2 * alpha)
            g = int(g1 * (1 - alpha) + g2 * alpha)
            b = int(b1 * (1 - alpha) + b2 * alpha)
            draw.line([(0, i), (size[0], i)], fill=(r, g, b))
        
        # Add text
        try:
            # Try to use a nice font
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        except:
            # Fallback to default
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw topic name
        text_bbox = draw.textbbox((0, 0), topic, font=font_large)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2 - 50
        
        # Add shadow
        draw.text((x + 3, y + 3), topic, font=font_large, fill='#00000080')
        draw.text((x, y), topic, font=font_large, fill=colors['text'])
        
        # Add subtitle
        subtitle = "Open Navigator"
        sub_bbox = draw.textbbox((0, 0), subtitle, font=font_small)
        sub_width = sub_bbox[2] - sub_bbox[0]
        sub_x = (size[0] - sub_width) // 2
        sub_y = y + text_height + 20
        draw.text((sub_x, sub_y), subtitle, font=font_small, fill=colors['text'])
        
        return img
    
    def create_square_image(self, topic: str, colors: dict, size: tuple = (400, 400)) -> Image.Image:
        """Create a square thumbnail image.
        
        Args:
            topic: Topic name
            colors: Color scheme dictionary
            size: Image size (width, height)
            
        Returns:
            PIL Image object
        """
        # Create image
        img = Image.new('RGB', size, colors['primary'])
        draw = ImageDraw.Draw(img)
        
        # Add circular gradient
        center_x, center_y = size[0] // 2, size[1] // 2
        max_radius = min(size) // 2
        
        for r in range(max_radius, 0, -1):
            alpha = r / max_radius
            r1, g1, b1 = tuple(int(colors['primary'][j:j+2], 16) for j in (1, 3, 5))
            r2, g2, b2 = tuple(int(colors['secondary'][j:j+2], 16) for j in (1, 3, 5))
            rc = int(r1 * alpha + r2 * (1 - alpha))
            gc = int(g1 * alpha + g2 * (1 - alpha))
            bc = int(b1 * alpha + b2 * (1 - alpha))
            draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], fill=(rc, gc, bc))
        
        # Add text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Wrap text if too long
        words = topic.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] < size[0] - 40:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw centered text
        total_height = len(lines) * 50
        y_start = (size[1] - total_height) // 2
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            width = bbox[2] - bbox[0]
            x = (size[0] - width) // 2
            y = y_start + i * 50
            # Shadow
            draw.text((x + 2, y + 2), line, font=font, fill='#00000080')
            draw.text((x, y), line, font=font, fill=colors['text'])
        
        return img
    
    def generate_images(self, topic: str, prefix: Optional[str] = None) -> dict:
        """Generate both banner and square images for a topic.
        
        Args:
            topic: Topic name
            prefix: Optional filename prefix (defaults to slugified topic)
            
        Returns:
            Dictionary with paths to generated images
        """
        # Generate color scheme
        print(f"\n🎨 Generating color scheme for: {topic}")
        colors = self.generate_color_scheme(topic)
        
        # Create filename-safe prefix
        if not prefix:
            prefix = topic.lower().replace(' ', '_').replace('&', 'and')
            prefix = ''.join(c for c in prefix if c.isalnum() or c == '_')
        
        # Generate banner
        print(f"🖼️  Creating banner image (1200x600)...")
        banner = self.create_banner_image(topic, colors)
        banner_path = self.output_dir / f"{prefix}_banner.png"
        banner.save(banner_path, quality=95)
        print(f"✅ Saved: {banner_path}")
        
        # Generate square
        print(f"🔲 Creating square image (400x400)...")
        square = self.create_square_image(topic, colors)
        square_path = self.output_dir / f"{prefix}_square.png"
        square.save(square_path, quality=95)
        print(f"✅ Saved: {square_path}")
        
        return {
            'topic': topic,
            'banner': str(banner_path),
            'square': str(square_path),
            'colors': colors
        }


def main():
    parser = argparse.ArgumentParser(description='Generate topic/cause images using Gemini')
    parser.add_argument('--topic', type=str, help='Single topic to generate images for')
    parser.add_argument('--topics-file', type=str, help='File with list of topics (one per line)')
    parser.add_argument('--output-dir', type=str, default='data/media/topics',
                       help='Output directory for images')
    parser.add_argument('--api-key', type=str, help='Google Gemini API key (or use GEMINI_API_KEY env var)')
    
    args = parser.parse_args()
    
    # Get topics list
    topics = []
    if args.topic:
        topics = [args.topic]
    elif args.topics_file:
        with open(args.topics_file, 'r') as f:
            topics = [line.strip() for line in f if line.strip()]
    else:
        # Default trending topics
        topics = [
            'World Press Freedom Day',
            'Business & Markets',
            'Artificial Intelligence',
            'Health & Medicine',
            'Social Media',
            'Civic Engagement',
            'Climate Action',
            'Education Reform',
            'Housing Policy',
            'Transportation'
        ]
        print("ℹ️  No topics specified, using default list")
    
    # Initialize generator
    try:
        generator = TopicImageGenerator(api_key=args.api_key, output_dir=args.output_dir)
    except ValueError as e:
        print(f"\n❌ {e}")
        print("\n💡 To use this script:")
        print("   1. Get a Gemini API key: https://makersuite.google.com/app/apikey")
        print("   2. Add to .env file: GEMINI_API_KEY=your_key_here")
        print("   3. Or pass with --api-key flag")
        return 1
    
    # Generate images for each topic
    results = []
    print(f"\n🚀 Generating images for {len(topics)} topics...\n")
    
    for i, topic in enumerate(topics, 1):
        print(f"\n[{i}/{len(topics)}] Processing: {topic}")
        print("=" * 60)
        try:
            result = generator.generate_images(topic)
            results.append(result)
        except Exception as e:
            print(f"❌ Error generating images for '{topic}': {e}")
            continue
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Successfully generated images for {len(results)}/{len(topics)} topics")
    print(f"📁 Images saved to: {args.output_dir}")
    
    # Save metadata
    metadata_path = Path(args.output_dir) / 'metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"📄 Metadata saved to: {metadata_path}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
