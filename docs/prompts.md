# Photographi MCP: Prompts & Features Guide

**Professional Visual Intelligence for AI-Powered Photography Workflows**

This guide demonstrates all capabilities of the Photographi MCP server and shows how AI assistants can leverage the tool outputs to help with real photography workflows.

> **Compatible with**: Gemini CLI, Claude Code CLI, GitHub Copilot CLI  
> **Supported Formats**: RAW (ARW, CR3, NEF, RAF, DNG, ORF) and standard formats (JPG, PNG, TIFF)

---

## 🎯 Feature 1: Photo Quality Analysis

**What it does**: Analyzes a single photo and returns comprehensive technical and aesthetic metrics.

**When to use**: Initial photo review, understanding technical issues, validating camera settings, preparing images for clients.

### Example Prompts

```
Analyze the photo quality of /path/to/photo.ARW
```

```
Give me a technical breakdown of my_portrait.JPG
```

```
What are the technical issues with this photo?
```

### Tool Output Structure

```json
{
  "judgement": "Excellent",
  "overallConfidence": 0.946,
  "technicalScore": 0.95,
  "aestheticScore": 0.98,
  "judgementDescription": "The technical integrity is rated as excellent. Sharpness is excellent. Exposure is well-balanced. Additional strengths include: good color balance, a wide dynamic range.",
  "description": "Image containing: couch, vase.",
  "metrics": {
    "sharpness": {"score": 1.0, "explanation": "Edges are sharp and directional."},
    "exposure": {"score": 0.98, "explanation": "Exposure is well-balanced."},
    "noise": {"score": 0.68, "explanation": "Noticeable sensor noise."},
    "color": {"score": 0.98, "explanation": "Natural color balance."},
    "dynamicRange": {"score": 0.97, "explanation": "Rich tonal information."},
    "focus": {"score": 0.85, "explanation": "Main subject 'vase' is in focus."}
  }
}
```

### How AI Assistants Use This

The AI can:
- **Explain technical quality** in photographer-friendly language
- **Identify specific issues** (noise, blur, clipping) and suggest solutions
- **Compare** against professional standards or client requirements
- **Recommend** camera settings adjustments for future shoots
- **Validate** if an image meets quality requirements for print/web

**Example AI Response Pattern**:
> "This photo scores 0.95/1.0 (Excellent). The sharpness is perfect at 1.0, ideal for large prints. However, the noise score of 0.68 indicates noticeable grain—you may want to reduce ISO in future shots or apply denoising in post-processing."

---

## 🏆 Feature 2: Photo Ranking & Comparison

**What it does**: Analyzes multiple photos in a folder and ranks them by quality, providing detailed technical summaries for each.

**When to use**: Selecting best shots from a burst sequence, culling a large shoot, finding hero images for portfolios, comparing similar compositions.

### Example Prompts

```
Rank all photos in /path/to/shoot by technical quality
```

```
Find the sharpest photo in this folder and tell me why it's the best
```

```
Compare all photos and rank them from best to worst with detailed explanations
```

```
Which photo has the highest overall quality score?
```

### Tool Output Structure

```json
{
  "status": "Ranking Complete",
  "totalImagesScanned": 4,
  "bestImages": [
    {
      "filename": "DSC00504.JPG",
      "score": 0.946,
      "judgement": "Excellent",
      "technicalScore": 0.95,
      "aestheticScore": 0.98,
      "summary": "The technical integrity is rated as excellent. Sharpness is excellent. Exposure is well-balanced. Additional strengths include: good color balance, a wide dynamic range.",
      "metrics": {
        "sharpness": 1.0,
        "exposure": 0.98,
        "noise": 0.68,
        "color": 0.98,
        "dynamicRange": 0.97,
        "focus": 0.85
      }
    }
  ]
}
```

### How AI Assistants Use This

The AI can:
- **Present rankings** in an easy-to-scan format with explanations
- **Compare and contrast** technical strengths/weaknesses between shots
- **Recommend the best image** for specific use cases (web vs. print, portfolio vs. social)
- **Group similar-quality images** for batch editing suggestions
- **Explain trade-offs** (e.g., "Photo A has better sharpness, but Photo B has superior dynamic range")

**Example AI Response Pattern**:
> "Here's your shoot ranked by quality:
> 1. **DSC00504.JPG** (0.95/1.0) - Best overall. Perfect sharpness (1.0) and excellent color balance (0.98). Minor noise at 0.68.
> 2. **DSC00505.ARW** (0.67/1.0) - Good technical quality. Main subject in focus but slightly noisier.
> 
> Recommendation: Use DSC00504.JPG as your hero image for the portfolio."

---

## 🗑️ Feature 3: Automated Photo Culling

**What it does**: Identifies low-quality photos and optionally moves them to a separate folder, preserving RAW+JPEG pairs.

**When to use**: Post-shoot organization, storage management, client delivery prep, automating rejection/selection workflows.

### Example Prompts

```
Cull photos with quality scores below 0.6 from /path/to/shoot
```

```
Identify any low-quality or blurry photos in this folder
```

```
Show me which photos would be rejected if I set a quality threshold of 0.5
```

```
Find all photos with excessive noise or blur and move them to a 'rejected' folder
```

### Tool Output Structure

```json
{
  "status": "Culling complete",
  "action": "moved",
  "totalImagesScanned": 120,
  "imagesCulled": 15,
  "threshold": 0.5,
  "culledImages": [
    {
      "filename": "IMG_1234.ARW",
      "score": 0.42,
      "reason": "Below threshold. Sharpness: 0.3 (blurry), Noise: 0.4 (excessive noise)."
    }
  ]
}
```

### How AI Assistants Use This

The AI can:
- **Summarize culling results** with statistics (e.g., "15 of 120 photos culled")
- **Explain why each photo was rejected** based on specific metric failures
- **Suggest threshold adjustments** if too many/few photos were culled
- **Provide batch editing tips** for borderline images
- **Confirm RAW+JPEG pairing** was preserved during moves

**Example AI Response Pattern**:
> "Culling complete! I moved 15 low-quality photos (quality < 0.5) to the 'rejected' folder. Key issues:
> - 8 photos: Severe blur (sharpness < 0.4)
> - 5 photos: Excessive noise (noise < 0.5)
> - 2 photos: Poor exposure (clipping detected)
> 
> You now have 105 keeper photos ready for editing. RAW+JPEG pairs were kept together."

---

## 🎨 Feature 4: Color Palette Extraction

**What it does**: Extracts dominant color palettes from photos for design, branding, or mood board creation.

**When to use**: Creating mood boards, matching brand colors, design inspiration, coordinating photo series, social media themes.

### Example Prompts

```
Extract a 5-color palette from /path/to/best_photo.jpg
```

```
Get color palettes from the top 3 photos in this folder
```

```
Find the most vibrant photo and give me its color palette
```

```
Create a mood board palette from my travel photos
```

### Tool Output Structure

```json
{
  "filename": "sunset_beach.jpg",
  "palette": [
    {"hex": "#E8A87C", "rgb": [232, 168, 124]},
    {"hex": "#C27662", "rgb": [194, 118, 98]},
    {"hex": "#5B9AA0", "rgb": [91, 154, 160]},
    {"hex": "#D4A76A", "rgb": [212, 167, 106]},
    {"hex": "#8B4F36", "rgb": [139, 79, 54]}
  ]
}
```

### How AI Assistants Use This

The AI can:
- **Display palettes visually** using color codes
- **Describe color moods** (warm, cool, earthy, vibrant, muted)
- **Suggest use cases** for each color (accent, background, contrast)
- **Compare palettes** across multiple photos for cohesive series
- **Match to brand guidelines** or design systems

**Example AI Response Pattern**:
> "Here's the 5-color palette from your sunset beach photo:
> 
> 🎨 **Warm Coral** (#E8A87C) - Perfect for backgrounds
> 🎨 **Terracotta** (#C27662) - Great accent color
> 🎨 **Ocean Teal** (#5B9AA0) - Provides cool contrast
> 🎨 **Sandy Gold** (#D4A76A) - Neutral highlight
> 🎨 **Rich Brown** (#8B4F36) - Grounding dark tone
> 
> This palette has a warm, sunset vibe perfect for coastal branding or summer campaigns."

---

## 📊 Feature 5: Batch Analysis & Reporting

**What it does**: Analyzes entire folders and generates comprehensive quality reports with statistics and insights.

**When to use**: Post-shoot reviews, quality control audits, client reporting, identifying systematic camera issues, portfolio curation.

### Example Prompts

```
Audit /path/to/wedding_shoot for technical issues
```

```
Give me a quality report for all images showing scores, issues, and detected subjects
```

```
Create a summary with average quality, best photo, and worst photo
```

```
Which photos have clipping issues in this folder?
```

### Tool Output Structure

```json
{
  "totalImages": 120,
  "averageQuality": 0.72,
  "bestPhoto": {"filename": "IMG_5678.ARW", "score": 0.95},
  "worstPhoto": {"filename": "IMG_1234.JPG", "score": 0.38},
  "commonIssues": [
    {"issue": "noise", "affectedPhotos": 45, "severity": "moderate"},
    {"issue": "blur", "affectedPhotos": 12, "severity": "severe"},
    {"issue": "clipping", "affectedPhotos": 8, "severity": "moderate"}
  ],
  "qualityDistribution": {
    "excellent": 25,
    "good": 60,
    "acceptable": 20,
    "poor": 10,
    "veryPoor": 5
  }
}
```

### How AI Assistants Use This

The AI can:
- **Generate executive summaries** for clients or team reviews
- **Visualize quality distributions** textually
- **Identify patterns** (e.g., "All low-light shots have noise issues")
- **Suggest workflow improvements** based on common issues
- **Prioritize editing work** by highlighting best candidates

**Example AI Response Pattern**:
> "**Wedding Shoot Quality Report**
> 
> 📸 Total Photos: 120  
> ⭐ Average Quality: 0.72/1.0 (Good)  
> 🏆 Best: IMG_5678.ARW (0.95 - Excellent sharpness, perfect for album cover)  
> ⚠️ Needs Review: 15 photos below 0.5 threshold
> 
> **Common Issues:**
> - Noise (45 photos) - Likely from high ISO during reception. Consider denoising in Lightroom.
> - Blur (12 photos) - Shutter speed may have been too slow. Review camera settings.
> 
> **Recommendation**: You have 85 keeper photos ready for delivery. Focus editing time on the top 25 'Excellent' shots for the album."

---

## 🎯 Understanding the Output

### Score Ranges & Meanings

| Score Range | Judgement | Meaning |
|-------------|-----------|---------|
| 0.80 - 1.00 | **Excellent** | Portfolio-quality, client delivery ready, no major issues |
| 0.65 - 0.79 | **Good** | Professional quality, minor issues, suitable for most uses |
| 0.50 - 0.64 | **Acceptable** | Usable but may need editing, not ideal for critical applications |
| 0.35 - 0.49 | **Poor** | Significant technical issues, consider rejecting or heavy editing |
| 0.00 - 0.34 | **Very Poor** | Major defects (severe blur, extreme noise), likely unusable |

### Key Metrics Explained

**Technical Score (0-1)**  
Weighted combination of sharpness, exposure, noise, color, and dynamic range. Represents the photo's technical execution.

**Aesthetic Score (0-1)**  
Based on composition rules, subject detection, color harmony, and visual balance. More subjective quality assessment.

**Sharpness (0-1)**  
Edge clarity and detail resolution. >0.8 = tack sharp, <0.4 = noticeably blurry.

**Exposure (0-1)**  
Histogram distribution and clipping detection. >0.85 = well-balanced, <0.5 = significant over/underexposure.

**Noise (0-1)**  
High-frequency grain and sensor noise. **Lower values = more noise**. >0.8 = clean, <0.5 = noticeable grain.

**Color (0-1)**  
White balance accuracy and color cast detection. >0.85 = neutral tones, <0.7 = color cast present.

**Dynamic Range (0-1)**  
Tonal information preservation from shadows to highlights. >0.85 = excellent detail retention.

**Focus (0-1, optional)**  
Only available when subject detection is enabled. Measures if the detected main subject is in sharp focus.

---

## 🚀 Advanced Usage Patterns

### Multi-Step Workflows

**Portfolio Curation**
```
1. Rank all photos in /portfolio_candidates
2. Filter to only those with scores above 0.8
3. Extract color palettes from the top 10
4. Group by similar color palettes for cohesive presentation
```

**Wedding Delivery Prep**
```
1. Audit /wedding_raw for technical issues
2. Cull photos below 0.6 quality
3. Rank remaining photos by quality
4. Extract palettes from ceremony photos for album design
5. Generate final report for client review
```

**Camera Settings Validation**
```
1. Analyze test shots from /camera_test at different ISOs
2. Compare noise scores across ISO ranges
3. Identify optimal ISO for your shooting conditions
```

### Combining with RAW+JPEG Workflows

The MCP automatically detects RAW+JPEG pairs (e.g., `DSC001.ARW` and `DSC001.JPG`) and keeps them together during culling operations.

**Tip**: RAW files typically score slightly lower than their JPEG counterparts due to less aggressive in-camera processing. This is expected and doesn't necessarily mean the RAW is inferior—it just needs editing.

---

## 💡 Pro Tips for AI Assistants

### Best Practices for LLMs Using This Tool

1. **Always show scores with context**: Don't just say "0.85"—explain that it's "Excellent (0.85/1.0)".

2. **Translate metrics to actions**: Instead of "sharpness: 0.3", say "This photo is significantly blurred—not suitable for large prints."

3. **Prioritize actionable insights**: Users want to know what to DO with the information, not just the numbers.

4. **Use comparisons effectively**: "Photo A has better sharpness (0.9 vs 0.6), but Photo B has superior color balance (0.95 vs 0.7)."

5. **Explain trade-offs**: "While the noise score is low (0.5), the sharpness is excellent (0.95)—you can denoise in post without losing detail."

6. **Group related issues**: If 30 photos all have noise issues, suggest "These appear to be from a low-light shoot—batch denoising would be effective."

7. **Respect photographer expertise**: Frame suggestions as options, not mandates. "Consider raising shutter speed for sharper action shots" vs "You must use 1/500s."

---

## 🎨 Example Use Cases by Photography Type

### Portrait Photography
- Find shots where subject's eyes are in perfect focus
- Identify images with flattering skin tones (color score >0.9)
- Cull unflattering expressions while preserving technical quality

### Landscape Photography
- Prioritize images with excellent dynamic range (>0.9) for HDR processing
- Find shots with optimal sharpness across the entire frame
- Extract color palettes for cohesive series presentation

### Wildlife/Sports Photography
- Rank burst sequences to find the decisive moment
- Filter for critical sharpness (>0.85) on fast-moving subjects
- Identify shots where main subject is in focus despite motion

### Wedding Photography
- Audit large shoots (500+ photos) for quick culling
- Ensure no critical moments are blurry before delivery
- Group by quality for album selection vs web gallery

### Product Photography
- Validate technical perfection (all scores >0.9) for e-commerce
- Ensure consistent color balance across product lines
- Detect exposure issues that would affect product appearance

---

## 📚 Additional Resources

- **Setup Guide**: [README.md](../README.md)
- **API Reference**: [MCP_REFERENCE.md](../MCP_REFERENCE.md)
- **Camera Compatibility**: [BRAND_TEST_GUIDE.md](../BRAND_TEST_GUIDE.md)
- **Troubleshooting**: [USER_JOURNEY.md](../USER_JOURNEY.md)

---

## 🤝 Contributing Prompts

Have a great prompt or use case? Contributions welcome! This is a living document designed to help photographers get the most out of AI-powered photo analysis.
