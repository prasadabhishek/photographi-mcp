# The Science of photographi

`photographi` is not just a file browser—it's a digital darkroom technician. It uses a combination of **Classical Signal Processing**, **Optical Physics**, and **Computer Vision** to judge your photos. 

Here is a breakdown of the "Science" behind every scorecard.

---

## 📸 1. Exposure: The Ansel Adams Zone System
Instead of just looking at "brightness," we divide the image histogram into 11 strictly defined "Zones" (0 to X).

- **The Problem**: A photo with a bright sky and dark ground might look "correct" on average, but contain no detail in the clouds.
- **The Solution**: We detect **non-recoverable clipping** in Zone 0 (Crushed Shadows) and Zone X (Blown Highlights). 
- **Subject-Aware Metering**: If the AI detects a person, we calculate the average luminance of their face and prioritize "Zone V" (18% Middle Gray) for that region. This is how we distinguish a stylistic silhouette from a poorly exposed portrait.

---

## 📐 2. Sharpness: FFT Anisotropy & Diffraction
We don't just look for "edges"—we analyze the **physics of light** through your lens.

- **FFT Analysis**: We perform a Fast Fourier Transform to move from pixels to "frequencies." High frequencies represent fine detail.
- **Anisotropy (Directionality)**: Sharp images have high-frequency energy that goes in specific directions (edges). Blurry images have uniform, low-frequency "smearing."
- **Diffraction Limited Aperture (DLA)**: Every camera has a point where the hole in the lens is so small that light begins to bend (diffraction), causing natural softening. `photographi` knows your camera's sensor size and pixel pitch. If you shoot at f/22, we might flag "Diffraction Limit Reached," letting you know the softness is a physical limit, not a lens failure.

---

## 🧬 3. Noise: ISO-Adaptive Chroma/Luma Weighting
Not all noise is created equal.

- **ISO-Adaptive**: We calculate the "Noise Floor" based on your ISO settings. We expect more grain at ISO 6400 than at ISO 100.
- **Chroma vs. Luma**: 
    - **Luma (Luminance)** is like film grain; it often looks organic.
    - **Chroma (Color)** is digital blotching; it looks ugly.
- **The Engine**: We heavily penalize color blotching (Chroma) while being more lenient on organic grain (Luma), ensuring your high-ISO "cinematic" shots are still rated highly.

---

## 🖼️ 4. Aesthetic Intelligence (AI ROI)
We use a **YOLOv11** neural network to identify the "Intent" of the photo.

- **Rule of Thirds**: We calculate the distance between your subject and the four "Power Points" of a frame.
- **Headroom Analysis**: For portraits, we judge how much space is left above the head. Too much looks like the person is drowning; too little looks like they are being crushed. We aim for the "Goldilocks Zone" of 8-20%.
- **Dynamic Range width**: We measure the **98th-Percentile Tonal Width**—how many distinct shades of gray your sensor actually managed to capture, ignoring outliers like noise.

---

## 🏁 The Overall Score
`overallConfidence = Technical_Score * (0.8 + 0.2 * Aesthetic_Score)`

This formula ensures that **Aesthetics cannot save a broken photo**. A beautifully composed shot that is out of focus will always receive a low score, while a technically perfect shot with average composition remains a "Keeper."
