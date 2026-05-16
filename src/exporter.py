# ======= • ======= • ======= • ======= • =======• =======
# Z-Image Pro — exporter.py
# Repository: https://github.com/Shineii86/ZImagePro
#
# @description
#   Output export utilities. Zips all generated PNG images
#   from the results directory and triggers a browser download
#   when running in Google Colab. Falls back to printing the
#   local zip path in non-Colab environments.
#
#   Matches notebook Cell 3's auto_download logic:
#     if auto_download:
#         from google.colab import files
#         files.download(str(save_path))
#
# @exports
#   zip_outputs, download_zip
#
# @version 1.0.0
# @author  Shinei Nouzen
# @license MIT
# ======= • ======= • ======= • ======= • =======• =======

import os
import subprocess

from . import log
from .config import RESULTS_DIR, PLATFORM

# ══════════════════════════════════════════════════════════════
# ARCHIVE
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: Zip generated images ----

def zip_outputs(
    output_dir=None,
    zip_path=None,
):
    """
    Zip all PNG files in the output directory.
    Creates the zip at the given path using the system zip command.
    Returns None and prints a warning if no images are found.

    @param {str} output_dir — Results output directory (auto-detected from platform)
    @param {str} zip_path — Destination zip file path (auto-detected from platform)
    @returns {str|None} Path to the created zip, or None if empty
    """
    if output_dir is None:
        output_dir = RESULTS_DIR
    if zip_path is None:
        root = os.path.dirname(RESULTS_DIR)
        zip_path = os.path.join(root, "Z_Image_Pro_Artworks.zip")

    if not os.path.exists(output_dir) or not os.listdir(output_dir):
        log.warn("No images found in the output directory yet!")
        return None

    log.info("🗜️ Zipping generated artworks...")
    png_files = [
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(".png")
    ]
    subprocess.run(["zip", "-j", "-q", zip_path, *png_files], check=True)
    log.success(f"Zipped to: {zip_path}")
    return zip_path


# ══════════════════════════════════════════════════════════════
# BROWSER DOWNLOAD
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: Colab file download trigger ----
# Notebook Cell 3: if auto_download: from google.colab import files; files.download(str(save_path))

def download_zip(zip_path=None):
    """
    Trigger a browser download of the zip file.
    Auto-detects platform:
      - Colab: uses google.colab.files API
      - Kaggle: prints path (download from sidebar)
      - Local: prints path for manual retrieval

    @param {str} zip_path — Path to the zip file (auto-detected)
    @returns {None}
    """
    if zip_path is None:
        root = os.path.dirname(RESULTS_DIR)
        zip_path = os.path.join(root, "Z_Image_Pro_Artworks.zip")

    if PLATFORM == "colab":
        try:
            from google.colab import files
            log.info("📥 Initiating download...")
            files.download(zip_path)
        except ImportError:
            log.warn(f"Zip saved at: {zip_path}")
    elif PLATFORM == "kaggle":
        log.info(f"📥 Zip ready: {zip_path}")
        log.info("   Download from the Kaggle sidebar → Output → Files")
    else:
        log.info(f"📥 Zip saved at: {zip_path}")


# ══════════════════════════════════════════════════════════════
# EXPORTS
# ══════════════════════════════════════════════════════════════

__all__ = ["zip_outputs", "download_zip"]

# ══════════════════════════════════════════════════════════════ END: exporter.py
