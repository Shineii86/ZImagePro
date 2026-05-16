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

from .config import WORKSPACE, DEFAULTS

# ══════════════════════════════════════════════════════════════
# STRUCTURED LOGGER
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: Logging ----

class _Log:
    """Structured logger with ISO timestamps."""

    @staticmethod
    def info(*args):
        print("[INFO]", *args)

    @staticmethod
    def warn(*args):
        print("[WARN]", *args)

    @staticmethod
    def error(*args):
        print("[ERROR]", *args)


log = _Log()

# ══════════════════════════════════════════════════════════════
# MODEL LOADER
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: In-process ComfyUI node loading ----

def load_models(unet_filename="z-image-turbo-fp8-e4m3fn.safetensors"):
    """
    Load UNet, CLIP, and VAE models into VRAM using ComfyUI nodes.
    Also initializes all required processing nodes.

    @param {str} unet_filename — UNet model file name
    @returns {tuple} (nodes_dict, unet_model, clip_model, vae_model)
    """
    from nodes import NODE_CLASS_MAPPINGS

    log.info("🧠 Loading models into VRAM...")

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

        unet_model = nodes["unet"].load_unet(unet_filename, "fp8_e4m3fn_fast")[0]
        clip_model = nodes["clip"].load_clip("qwen_3_4b.safetensors", type="lumina2")[0]
        vae_model  = nodes["vae"].load_vae("ae.safetensors")[0]

    log.info("✅ Engine Online. Ready to Generate.")
    return nodes, unet_model, clip_model, vae_model


# ══════════════════════════════════════════════════════════════
# IMAGE GENERATOR
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: End-to-end image generation ----

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

    Encodes positive/negative prompts via CLIP, creates an empty
    latent, runs KSampler denoising, decodes through VAE, and
    saves the result as PNG.

    @param {dict} nodes — ComfyUI node instances from load_models()
    @param {object} unet_model — Loaded UNet model
    @param {object} clip_model — Loaded CLIP model
    @param {object} vae_model — Loaded VAE model
    @param {str} prompt — Positive prompt text
    @param {str} negative_prompt — Negative prompt text
    @param {int} width — Image width in pixels
    @param {int} height — Image height in pixels
    @param {int} steps — Sampling steps
    @param {float} cfg — CFG scale
    @param {str} sampler_name — KSampler algorithm name
    @param {str} scheduler — Noise schedule type
    @param {int} seed — RNG seed (-1 = random)
    @param {str} save_dir — Output directory (defaults to /content/results)
    @returns {tuple} (PIL.Image, save_path)
    """
    if save_dir is None:
        save_dir = os.path.join(os.path.dirname(WORKSPACE), "results")
    os.makedirs(save_dir, exist_ok=True)

    gen_seed = torch.randint(0, 2**63 - 1, (1,)).item() if seed == -1 else seed

    # ─── Flush VRAM ───
    gc.collect()
    torch.cuda.empty_cache()

    log.info(f"➜ Generating: {width}x{height} | Steps: {steps} | Seed: {gen_seed}")

    with torch.inference_mode():
        # ─── Encode ───
        pos_enc = nodes["enc"].encode(clip_model, prompt)[0]
        neg_enc = nodes["enc"].encode(clip_model, negative_prompt)[0]
        latent  = nodes["empty"].generate(width, height, batch_size=1)[0]

        # ─── Sample ───
        sample = nodes["sampler"].sample(
            unet_model, gen_seed, steps, cfg,
            sampler_name, scheduler, pos_enc, neg_enc, latent, denoise=1.0
        )[0]

        # ─── Decode ───
        decoded = nodes["decode"].decode(vae_model, sample)[0].detach()

    # ─── Save & Return ───
    img_out = Image.fromarray(np.array(decoded * 255, dtype=np.uint8)[0])

    clean_prompt = re.sub(r'[^a-zA-Z0-9_-]', '_', prompt)[:20]
    filename = f"{clean_prompt}_{uuid.uuid4().hex[:4]}.png"
    save_path = os.path.join(save_dir, filename)
    img_out.save(save_path)

    log.info(f"✅ Saved to: {filename}")
    return img_out, save_path


# ══════════════════════════════════════════════════════════════
# EXPORTS
# ══════════════════════════════════════════════════════════════

__all__ = ["load_models", "generate_image"]

# ══════════════════════════════════════════════════════════════ END: generator.py
