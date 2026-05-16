# 📖 Z-Image Turbo Pro — User Guide

A comprehensive beginner-friendly guide for the Z-Image Turbo Pro Colab notebook.

---

## Table of Contents

1. [What Is This?](#what-is-this)
2. [What Is Google Colab?](#what-is-google-colab)
3. [What Is a Notebook?](#what-is-a-notebook)
4. [Getting Started](#getting-started)
5. [Step-by-Step Walkthrough](#step-by-step-walkthrough)
6. [Understanding the Settings](#understanding-the-settings)
7. [Resolutions Explained](#resolutions-explained)
8. [Samplers & Schedulers](#samplers--schedulers)
9. [Writing Good Prompts](#writing-good-prompts)
10. [Where Are My Files?](#where-are-my-files)
11. [FAQ](#faq)
12. [Troubleshooting](#troubleshooting)

---

## What Is This?

Z-Image Turbo Pro is a **text-to-image generator**. You type a description (a "prompt"), and the AI creates an image matching that description. It runs entirely on Google's free cloud GPUs — no powerful computer needed on your end.

The model used is **Z-Image Turbo FP8** — a state-of-the-art diffusion model quantized to FP8 format for efficient GPU usage.

---

## What Is Google Colab?

**Google Colab** (colab.research.google.com) is a free online platform where you can run Python code in the cloud. Think of it as a Google Doc, but for code — with a free GPU attached.

Key points:
- **Free tier** gives you a T4 GPU (16 GB VRAM) — enough for this notebook
- **No installation** — everything runs in your browser
- **Sessions are temporary** — files are deleted when you disconnect
- **GPU runtime** — you must select "T4 GPU" as the runtime type

---

## What Is a Notebook?

A **notebook** is a document with cells. Each cell is either:
- **Markdown** — formatted text (like this guide)
- **Code** — executable Python code

You run cells one at a time by clicking the ▶️ play button next to each cell, or press `Shift+Enter`.

---

## Getting Started

### Prerequisites
- A Google account (for Colab)
- A modern browser (Chrome recommended)
- Stable internet connection (for downloading models)

### First-Time Setup

1. **Open the notebook** — click the "Open in Colab" badge in the README
2. **Set runtime to T4 GPU**:
   - Go to `Runtime` → `Change runtime type`
   - Select `T4 GPU` from the dropdown
   - Click `Save`
3. **Run Cell 1** — click ▶️ or press `Shift+Enter`
   - This clones the repo, installs dependencies, and downloads models (~5 min first time)
4. **Run Cell 2** — configure your prompt and generate
5. **Run Cell 3** — download your results

---

## Step-by-Step Walkthrough

### Cell 1 — Initialize 🛠️

**What it does:**
- Clones the ZImagePro repository (provides the `src/` modules)
- Clones ComfyUI (the AI pipeline engine)
- Installs Python dependencies (torch, xformers, etc.)
- Installs aria2c (fast download accelerator)
- Downloads 3 model files:
  - **Z-Image Turbo FP8** (~4 GB) — the main AI model
  - **Qwen 3 4B** (~2.5 GB) — text encoder (understands your prompts)
  - **VAE** (~300 MB) — converts AI output to viewable images

**Duration:** ~5-8 minutes first run, ~30 seconds after (models are cached)

**What you'll see:**
```
🚀 Initializing Core Architecture...
   ✓ Core Engine Cloned
📦 Installing Dependencies (This takes a moment)...
📥 Fetching Models...
   📥 Fetching: z-image-turbo-fp8-e4m3fn.safetensors...
   ✓ Saved as: z-image-turbo-fp8-e4m3fn.safetensors
   ...
✅ Environment Ready! Please load the engine below.
```

### Cell 2 — Load Engine 🚀

**What it does:**
- Loads all 3 models into GPU VRAM
- Encodes your prompt via CLIP (text understanding)
- Runs the diffusion process (KSampler)
- Decodes the result through VAE
- Saves and displays the generated image

**Settings you can change:**
- `positive_prompt` — what you want to see
- `negative_prompt` — what to avoid
- `aspect_ratio` — image dimensions
- `steps` — quality vs speed
- `guidance_scale` — how closely to follow the prompt
- `seed` — for reproducible results

### Cell 3 — Creator Studio 🎨

**What it does:**

The Creator Studio cell is where you configure your prompt and generation settings, then run the image generation. It uses the `generate_image()` function from `src/generator.py`.

**Settings you can change:**
- `positive_prompt` — describe what you want to see
- `negative_prompt` — what to avoid
- `aspect_ratio` — image dimensions (1:1, 16:9, 9:16, 4:3, 21:9)
- `steps` — denoising iterations (10–50, default 20)
- `guidance_scale` — prompt adherence (1.0–10.0, default 1)
- `seed` — RNG seed (-1 = random)
- `auto_download` — auto-download after generation

### Cell 4 — Export 💾

**What it does:**
- Zips all generated PNG images
- Triggers a browser download of the zip file

---

## Understanding the Settings

### Prompt Settings

| Setting | What It Does | Tips |
|---------|-------------|------|
| **positive_prompt** | Describes what you want in the image | Be specific! Include style, lighting, mood |
| **negative_prompt** | Describes what to avoid | "blurry, low quality, text, watermark, distorted" is a good default |

### Image Settings

| Setting | Range | Default | What It Does |
|---------|-------|---------|-------------|
| **aspect_ratio** | Dropdown | 16:9 | Shape of the image |
| **steps** | 10-50 | 20 | More steps = more detail, but slower |
| **guidance_scale** | 1.0-10.0 | 1.0 | Higher = follows prompt more strictly |
| **seed** | -1 to ∞ | -1 | -1 = random each time. Same seed = same image |

### Advanced Settings

| Setting | Default | What It Does |
|---------|---------|-------------|
| **auto_download** | False | Automatically download after generation |

---

## Resolutions Explained

| Ratio | Resolution | Best For | Pixels |
|:-----:|:----------:|----------|--------|
| **1:1** | 1024×1024 | Profile pictures, social media posts | 1.05 MP |
| **16:9** | 1280×720 | YouTube thumbnails, desktop wallpapers | 0.92 MP |
| **9:16** | 720×1280 | Phone wallpapers, Instagram/TikTok stories | 0.92 MP |
| **4:3** | 1152×864 | Classic photo style, presentations | 1.00 MP |
| **21:9** | 1344×576 | Ultrawide monitors, cinematic shots | 0.77 MP |

**Tips:**
- The model was trained at 1024×1024 — this gives the best quality
- Other resolutions work well but may have slight quality differences
- Portrait (9:16) is great for character art
- Landscape (16:9) is great for scenery

---

## Samplers & Schedulers

### What's a Sampler?
The **sampler** is the algorithm that converts random noise into your image. Different samplers have different speed/quality tradeoffs.

### What's a Scheduler?
The **scheduler** controls how noise is reduced at each step. It affects the "style" of the denoising process.

### Best Settings for Z-Image Turbo

| Parameter | Recommended | Why |
|-----------|-------------|-----|
| **sampler** | `euler` | Fast, clean, well-tested with this model |
| **scheduler** | `simple` | Works best with Z-Image Turbo's architecture |
| **steps** | 20 | Sweet spot for quality vs speed |
| **cfg** | 1.0 | Low CFG works well with this model |

---

## Writing Good Prompts

### Structure
A good prompt follows this pattern:
```
[subject] + [details] + [style] + [quality]
```

### Examples

**❌ Bad:** "a cat"
**✅ Good:** "a fluffy orange cat sleeping on a stack of books, cozy rainy day, warm indoor lighting, watercolor illustration style, pastel colors, adorable"

**❌ Bad:** "city"
**✅ Good:** "a breathtaking cyberpunk cityscape at night, neon lights reflecting on wet streets, volumetric fog, cinematic lighting, ultra detailed, 8k"

### Power Words

| Category | Words to Use |
|----------|-------------|
| **Quality** | masterpiece, best quality, highly detailed, ultra detailed, 8k |
| **Lighting** | cinematic lighting, golden hour, volumetric fog, god rays, rim light |
| **Style** | oil painting, watercolor, anime, photorealistic, concept art, artstation |
| **Mood** | dramatic, ethereal, cozy, epic, serene, mysterious |
| **Camera** | close-up, wide angle, bird's eye view, macro, depth of field |

---

## Where Are My Files?

| Location | What's There |
|----------|-------------|
| `/content/results/` | Generated PNG images |
| `/content/Z_Image_Pro_Artworks.zip` | Zipped download package |
| `/content/ComfyUI/models/` | Downloaded model files (cached) |
| `/content/ZImagePro/` | Cloned repository with src/ modules |

**Note:** All files are deleted when your Colab session ends. Download your images before disconnecting!

---

## FAQ

**Q: Do I need a GPU?**
A: Not on your computer. Colab provides a free T4 GPU in the cloud.

**Q: How long does it take?**
A: First run: ~8 min (downloads). After that: ~30 seconds per image.

**Q: Can I generate multiple images?**
A: Yes! Just change the prompt or seed and run Cell 2 again. All images save to `/content/results/`.

**Q: What happens if I disconnect?**
A: All files are deleted. Download your images first! Run Cell 3 to zip and download.

**Q: Can I use this locally?**
A: Yes, if you have a GPU with 16GB+ VRAM. Clone the repo, install requirements, and use the `src/` modules directly.

**Q: Is there a content filter?**
A: No. Z-Image is an unfiltered model. You are responsible for the content you generate.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `CUDA out of memory` | Resolution too high or session overloaded | Reduce resolution, restart runtime |
| `No module named 'nodes'` | ComfyUI not cloned | Re-run Cell 1 |
| `No module named 'src'` | ZImagePro repo not cloned | Re-run Cell 1 |
| Download fails | Network issue | Check connection, re-run Cell 1 |
| Colab disconnects | Idle timeout or session limit | Stay active, or upgrade to Colab Pro |
| Image is black or garbled | Wrong model loaded | Ensure you're using Z-Image Turbo FP8 |
| `FP8 not supported` | GPU doesn't support FP8 | Try T4 or A100 runtime |
