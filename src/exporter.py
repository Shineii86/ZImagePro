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

# ══════════════════════════════════════════════════════════════
# ARCHIVE
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: Zip generated images ----

def zip_outputs(
    output_dir="/content/results",
    zip_path="/content/Z_Image_Pro_Artworks.zip",
):
    """
    Zip all PNG files in the output directory.
    Creates the zip at the given path using the system zip command.
    Returns None and prints a warning if no images are found.

    @param {str} output_dir — Results output directory (matches notebook's SAVE_DIR)
    @param {str} zip_path — Destination zip file path
    @returns {str|None} Path to the created zip, or None if empty
    """
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

def download_zip(zip_path="/content/Z_Image_Pro_Artworks.zip"):
    """
    Trigger a browser download of the zip file.
    Uses google.colab.files API when available, otherwise
    prints the local path for manual retrieval.

    Matches notebook: from google.colab import files; files.download(str(save_path))

    @param {str} zip_path — Path to the zip file
    @returns {None}
    """
    try:
        from google.colab import files
        log.info("📥 Initiating download...")
        files.download(zip_path)
    except ImportError:
        log.warn(f"Not running in Colab. Zip saved at: {zip_path}")


# ══════════════════════════════════════════════════════════════
# EXPORTS
# ══════════════════════════════════════════════════════════════

__all__ = ["zip_outputs", "download_zip"]

# ══════════════════════════════════════════════════════════════ END: exporter.py
