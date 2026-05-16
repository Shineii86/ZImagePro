# ======= • ======= • ======= • ======= • =======• =======
# Z-Image Pro — generator.py
# Repository: https://github.com/Shineii86/ZImagePro
#
# @description
#   ComfyUI node-based image generator. Loads UNet, CLIP, and
#   VAE models in-process, encodes prompts, samples latents
#   via KSampler, and decodes final images. Operates directly
#   in the notebook environment without a server — lightweight
#   and fast for single-session Colab usage.
#
#   Every function and parameter maps directly to notebook cells:
#   - load_models()    → Cell 2 (Load Engine)
#   - generate_image() → Cell 3 (Creator Studio)
#
# @exports
#   load_models, generate_image
#
# @version 1.0.0
# @author  Shinei Nouzen
# @license MIT
# ======= • ======= • ======= • ======= • =======• =======

import os
import re
import uuid
import gc

import torch
import numpy as np
from PIL import Image

from . import log
from .config import WORKSPACE, RESULTS_DIR, DEFAULTS

# ══════════════════════════════════════════════════════════════
# MODEL LOADER
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: In-process ComfyUI node loading ----
# Notebook Cell 2: NODE_CLASS_MAPPINGS → 7 nodes → load_unet/load_clip/load_vae

def _check_cuda():
    """
    Pre-flight check: verify CUDA-enabled PyTorch is available.
    Raises a clear, actionable error if CUDA is missing.

    @raises RuntimeError — if PyTorch was not compiled with CUDA support
    """
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError(
            "\n"
            "   ✗ CUDA is not available!\n"
            "\n"
            "   PyTorch installed without CUDA support. This usually means:\n"
            "     1. The Colab runtime is set to CPU — change it to T4:\n"
            "        Runtime → Change runtime type → T4 GPU\n"
            "     2. A CPU-only PyTorch was cached — restart runtime and re-run Cell 1\n"
            "\n"
            "   Fix: Runtime → Disconnect and delete runtime → Re-run all cells\n"
        )


def load_models(unet_filename="z-image-turbo-fp8-e4m3fn.safetensors"):
    """
    Load UNet, CLIP, and VAE models into VRAM using ComfyUI nodes.
    Also initializes all required processing nodes.

    Matches notebook Cell 2 exactly:
        nodes = {
            "unet": NODE_CLASS_MAPPINGS["UNETLoader"](),
            "clip": NODE_CLASS_MAPPINGS["CLIPLoader"](),
            "vae":  NODE_CLASS_MAPPINGS["VAELoader"](),
            "enc":  NODE_CLASS_MAPPINGS["CLIPTextEncode"](),
            "sampler": NODE_CLASS_MAPPINGS["KSampler"](),
            "decode": NODE_CLASS_MAPPINGS["VAEDecode"](),
            "empty": NODE_CLASS_MAPPINGS["EmptyLatentImage"]()
        }
        unet_model = nodes["unet"].load_unet("z-image-turbo-fp8-e4m3fn.safetensors", "fp8_e4m3fn_fast")[0]
        clip_model = nodes["clip"].load_clip("qwen_3_4b.safetensors", type="lumina2")[0]
        vae_model  = nodes["vae"].load_vae("ae.safetensors")[0]

    @param {str} unet_filename — UNet model file name
    @returns {tuple} (nodes_dict, unet_model, clip_model, vae_model)
    """
    _check_cuda()

    from nodes import NODE_CLASS_MAPPINGS

    log.info("Booting ComfyUI Backend...")

    with torch.inference_mode():
        nodes = {
            "unet":    NODE_CLASS_MAPPINGS["UNETLoader"](),
            "clip":    NODE_CLASS_MAPPINGS["CLIPLoader"](),
            "vae":     NODE_CLASS_MAPPINGS["VAELoader"](),
            "enc":     NODE_CLASS_MAPPINGS["CLIPTextEncode"](),
            "sampler": NODE_CLASS_MAPPINGS["KSampler"](),
            "decode":  NODE_CLASS_MAPPINGS["VAEDecode"](),
            "empty":   NODE_CLASS_MAPPINGS["EmptyLatentImage"](),
        }

        print("   ⏳ Loading Checkpoints into VRAM...", end="\r")
        unet_model = nodes["unet"].load_unet(unet_filename, "fp8_e4m3fn_fast")[0]
        clip_model = nodes["clip"].load_clip("qwen_3_4b.safetensors", type="lumina2")[0]
        vae_model  = nodes["vae"].load_vae("ae.safetensors")[0]

    log.success("Engine Online. Ready to Generate.")
    return nodes, unet_model, clip_model, vae_model


# ══════════════════════════════════════════════════════════════
# IMAGE GENERATOR
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: End-to-end image generation ----
# Notebook Cell 3: encode → sample → decode → save → display

def generate_image(
    nodes,
    unet_model,
    clip_model,
    vae_model,
    prompt,
    negative_prompt=DEFAULTS["negative_prompt"],
    width=DEFAULTS["width"],
    height=DEFAULTS["height"],
    steps=DEFAULTS["steps"],
    cfg=DEFAULTS["cfg"],
    sampler_name=DEFAULTS["sampler_name"],
    scheduler=DEFAULTS["scheduler"],
    seed=DEFAULTS["seed"],
    save_dir=None,
):
    """
    Generate a single image from a text prompt.

    Matches notebook Cell 3 (Creator Studio) exactly:
        gen_seed = torch.randint(0, 2**63 - 1, (1,)).item() if seed == -1 else seed
        flush_mem()
        with torch.inference_mode():
            pos_enc = nodes["enc"].encode(clip_model, positive_prompt)[0]
            neg_enc = nodes["enc"].encode(clip_model, negative_prompt)[0]
            latent  = nodes["empty"].generate(w, h, batch_size=1)[0]
            sample  = nodes["sampler"].sample(
                unet_model, gen_seed, steps, guidance_scale,
                "euler", "simple", pos_enc, neg_enc, latent, denoise=1.0
            )[0]
            decoded = nodes["decode"].decode(vae_model, sample)[0].detach()
        img_out = Image.fromarray(np.array(decoded * 255, dtype=np.uint8)[0])

    @param {dict} nodes — ComfyUI node instances from load_models()
    @param {object} unet_model — Loaded UNet model
    @param {object} clip_model — Loaded CLIP model
    @param {object} vae_model — Loaded VAE model
    @param {str} prompt — Positive prompt text
    @param {str} negative_prompt — Negative prompt text
    @param {int} width — Image width in pixels
    @param {int} height — Image height in pixels
    @param {int} steps — Sampling steps (10–50, default 20)
    @param {float} cfg — CFG scale (1.0–10.0, default 1)
    @param {str} sampler_name — KSampler algorithm name (default "euler")
    @param {str} scheduler — Noise schedule type (default "simple")
    @param {int} seed — RNG seed (-1 = random via torch.randint)
    @param {str} save_dir — Output directory (defaults to /content/results)
    @returns {tuple} (PIL.Image, save_path)
    """
    if save_dir is None:
        save_dir = RESULTS_DIR
    os.makedirs(save_dir, exist_ok=True)

    # Notebook: gen_seed = torch.randint(0, 2**63 - 1, (1,)).item() if seed == -1 else seed
    gen_seed = torch.randint(0, 2**63 - 1, (1,)).item() if seed == -1 else seed

    # Notebook: flush_mem() → gc.collect() + torch.cuda.empty_cache()
    gc.collect()
    torch.cuda.empty_cache()

    log.info(f"Generating: {width}x{height} | Steps: {steps} | Seed: {gen_seed}")

    # Notebook: # IMPORTANT: Use inference_mode to avoid tensor version errors during decoding
    with torch.inference_mode():
        # ─── Encode (Cell 3 L35-36) ───
        pos_enc = nodes["enc"].encode(clip_model, prompt)[0]
        neg_enc = nodes["enc"].encode(clip_model, negative_prompt)[0]

        # ─── Latent (Cell 3 L37) ───
        latent = nodes["empty"].generate(width, height, batch_size=1)[0]

        # ─── Sample (Cell 3 L40-43) ───
        # KSampler params: unet, seed, steps, cfg, sampler, scheduler, pos, neg, latent, denoise
        sample = nodes["sampler"].sample(
            unet_model, gen_seed, steps, cfg,
            sampler_name, scheduler, pos_enc, neg_enc, latent, denoise=1.0
        )[0]

        # ─── Decode (Cell 3 L46) ───
        decoded = nodes["decode"].decode(vae_model, sample)[0].detach()

    # ─── Save (Cell 3 L49-51) ───
    # Notebook: img_out = Image.fromarray(np.array(decoded * 255, dtype=np.uint8)[0])
    img_out = Image.fromarray(np.array(decoded * 255, dtype=np.uint8)[0])

    # Notebook: clean_promt = re.sub(r'[^a-zA-Z0-9_-]', '_', prompt)[:20]
    clean_prompt = re.sub(r'[^a-zA-Z0-9_-]', '_', prompt)[:20]
    # Notebook: filename = f"{clean_promt}_{uuid.uuid4().hex[:4]}.png"
    filename = f"{clean_prompt}_{uuid.uuid4().hex[:4]}.png"
    save_path = os.path.join(save_dir, filename)
    img_out.save(save_path)

    log.success(f"Saved to: {filename}")
    return img_out, save_path


# ══════════════════════════════════════════════════════════════
# EXPORTS
# ══════════════════════════════════════════════════════════════

__all__ = ["load_models", "generate_image"]

# ══════════════════════════════════════════════════════════════ END: generator.py
