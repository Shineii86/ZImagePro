# ======= • ======= • ======= • ======= • =======• =======
# Z-Image Pro — config.py
# Repository: https://github.com/Shineii86/ZImagePro
#
# @description
#   All configuration constants, default generation parameters,
#   model URLs, directory maps, and supported option lists.
#   Every tunable value the pipeline uses lives here.
#
# @exports
#   WORKSPACE, TEXT_ENCODER_URL, VAE_URL,
#   MODEL_DIRS, DEFAULTS, RESOLUTIONS, SAMPLERS, SCHEDULERS
#
# @version 1.0.0
# @author  Shinei Nouzen
# @license MIT
# ======= • ======= • ======= • ======= • =======• =======

# ══════════════════════════════════════════════════════════════
# PATHS
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: Workspace root ----
WORKSPACE = "/content/ComfyUI"

# ══════════════════════════════════════════════════════════════
# MODEL URLS
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: Pre-configured model download URLs ----
UNET_URL = "https://huggingface.co/T5B/Z-Image-Turbo-FP8/resolve/main/z-image-turbo-fp8-e4m3fn.safetensors"
TEXT_ENCODER_URL = "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors"
VAE_URL = "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors"

# ══════════════════════════════════════════════════════════════
# DIRECTORY MAP
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: Model subdirectories (relative to WORKSPACE) ----
MODEL_DIRS = {
    "unet": "models/diffusion_models",
    "clip": "models/clip",
    "vae":  "models/vae",
}

# ══════════════════════════════════════════════════════════════
# DEFAULT GENERATION PARAMETERS
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: Sensible defaults for image generation ----
DEFAULTS = {
    "width":           1024,
    "height":          1024,
    "batch_size":      1,
    "steps":           20,
    "cfg":             1.0,
    "sampler_name":    "euler",
    "scheduler":       "simple",
    "seed":            -1,
    "negative_prompt": "blurry, low quality, text, watermark, distorted",
}

# ══════════════════════════════════════════════════════════════
# RESOLUTION PRESETS
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: Aspect ratio → (width, height) mapping ----
RESOLUTIONS = {
    "1:1":  (1024, 1024),
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "4:3":  (1152, 864),
    "21:9": (1344, 576),
}

# ══════════════════════════════════════════════════════════════
# SUPPORTED SAMPLERS & SCHEDULERS
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: Available KSampler options ----
SAMPLERS = [
    "euler", "euler_ancestral", "heun", "dpm_2", "dpm_2_ancestral",
    "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral",
    "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde",
    "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu",
    "ddpm", "lcm", "ddim", "uni_pc", "uni_pc_bh2", "res_multistep",
]

# ---- FEATURE: Available scheduler options ----
SCHEDULERS = [
    "normal", "karras", "exponential", "sgm_uniform",
    "simple", "ddim_uniform", "beta",
]

# ══════════════════════════════════════════════════════════════ END: config.py
