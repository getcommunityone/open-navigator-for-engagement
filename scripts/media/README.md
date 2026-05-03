# Media Generation Scripts

Scripts for generating images, banners, and visual assets for topics, causes, and content.

## 📸 generate_topic_images.py

Generate professional banner images (1200x600) and square thumbnails (400x400) for trending topics and causes using Google Gemini AI.

### Features

- **AI-Powered Color Schemes**: Uses Gemini to suggest professional, thematic color palettes
- **Banner Images**: 1200x600px hero images for featured stories
- **Square Thumbnails**: 400x400px images for topic tiles and cards
- **Gradient Backgrounds**: Professional gradient effects
- **Smart Text Wrapping**: Automatically wraps long topic names
- **Batch Processing**: Generate images for multiple topics at once

### Setup

1. **Get a Gemini API Key**:
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key

2. **Add to .env file**:
   ```bash
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Install dependencies** (automatic):
   ```bash
   # The script will auto-install if needed:
   # - google-generativeai
   # - pillow
   # - requests
   ```

### Usage

**Generate for a single topic:**
```bash
python scripts/media/generate_topic_images.py --topic "World Press Freedom Day"
```

**Generate for multiple topics from a file:**
```bash
# Create topics.txt with one topic per line
echo "Artificial Intelligence" > topics.txt
echo "Health & Medicine" >> topics.txt
echo "Climate Action" >> topics.txt

python scripts/media/generate_topic_images.py --topics-file topics.txt
```

**Generate default trending topics:**
```bash
# No arguments = generates default set of 10 trending topics
python scripts/media/generate_topic_images.py
```

**Custom output directory:**
```bash
python scripts/media/generate_topic_images.py \
  --topic "Education Reform" \
  --output-dir frontend/public/images/topics
```

### Output

For each topic, generates:

1. **Banner**: `{topic_slug}_banner.png` (1200x600)
   - Hero image for featured stories
   - Professional gradient background
   - Large centered text with shadow

2. **Square**: `{topic_slug}_square.png` (400x400)
   - Thumbnail for topic cards
   - Circular gradient effect
   - Wrapped text for long names

3. **Metadata**: `metadata.json`
   - Color schemes used
   - File paths
   - Topic information

### Example Output

```
data/media/topics/
├── world_press_freedom_day_banner.png
├── world_press_freedom_day_square.png
├── artificial_intelligence_banner.png
├── artificial_intelligence_square.png
├── health_and_medicine_banner.png
├── health_and_medicine_square.png
└── metadata.json
```

### Default Topics

The script generates images for these topics by default:
- World Press Freedom Day
- Business & Markets
- Artificial Intelligence
- Health & Medicine
- Social Media
- Civic Engagement
- Climate Action
- Education Reform
- Housing Policy
- Transportation

### Color Scheme Examples

Gemini generates contextual color schemes:
- **Politics**: Professional blues and reds
- **Health**: Calming greens and blues
- **Technology**: Modern purples and blues
- **Sports**: Energetic oranges and reds
- **Environment**: Earth tones and greens

### Integration with Homepage

The generated images can be used in the homepage:

```typescript
// Update TOP_STORIES in Home.tsx
const TOP_STORIES = [
  {
    title: 'AI Policy Tracking',
    topic: 'Artificial Intelligence',
    image: '/images/topics/artificial_intelligence_square.png', // Use generated image
    link: '/search?q=artificial+intelligence'
  },
  // ...
]
```

### Troubleshooting

**"GEMINI_API_KEY not found"**
- Add your API key to `.env` file
- Or pass with `--api-key` flag

**Font errors**
- Script will fallback to default fonts
- On Linux: `sudo apt-get install fonts-dejavu`

**Low quality images**
- Images are saved at 95% quality
- For higher quality, edit the `quality` parameter in the script

### Future Enhancements

- [ ] Support for Imagen 2 (when available in Gemini API)
- [ ] Custom icon/emoji overlays
- [ ] Animation support (GIF/WebP)
- [ ] Social media sized variants (Twitter, Facebook, etc.)
- [ ] Watermark support
- [ ] Bulk export to CDN

## 🎨 Color Scheme Philosophy

The generator uses AI to create professional, accessible color schemes:

1. **High Contrast**: Ensures text readability (WCAG AA compliant)
2. **Thematic Relevance**: Colors match topic context
3. **Brand Consistency**: Works with Open Navigator's primary colors
4. **Professional Look**: News/media-appropriate palettes

## 📝 Notes

- Images are generated programmatically (no API image generation yet)
- Gemini is used for intelligent color scheme selection
- All images are optimized for web use
- Supports batch generation for efficiency
