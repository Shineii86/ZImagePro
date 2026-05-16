# ======= • ======= • ======= • ======= • =======• =======
# Z-Image Pro — downloader.py
# Repository: https://github.com/Shineii86/ZImagePro
#
# @description
#   Asset downloader with aria2c acceleration. Handles direct
#   HTTP(S) downloads, Google Drive links (via gdown), and
#   Civitai content-disposition URLs. Parallel chunk downloading
#   with 16 connections per file for maximum throughput.
#
#   Matches the notebook's model_map download logic:
#   - aria2c --console-log-level=error -c -x 16 -s 16 -k 1M
#   - Supports direct URLs, Google Drive, Civitai
#
# @exports
#   ensure_aria2, download_file, process_downloads
#
# @version 1.0.0
# @author  Shinei Nouzen
# @license MIT
# ======= • ======= • ======= • ======= • =======• =======

import os
import shutil
import subprocess
import urllib.parse

try:
    import gdown
except ImportError:
    gdown = None

from . import log
from .config import DRIVE_CACHE_DIR

# ══════════════════════════════════════════════════════════════
# ENVIRONMENT SETUP
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: Google Drive mount + cache helpers ----

def mount_drive():
    """
    Mount Google Drive at /content/drive if not already mounted.
    Returns True if Drive is available, False otherwise.

    @returns {bool}
    """
    if os.path.isdir("/content/drive/MyDrive"):
        return True
    try:
        from google.colab import drive
        log.info("   📂 Mounting Google Drive...")
        drive.mount("/content/drive", force_remount=False)
        return True
    except Exception as e:
        log.warn(f"   Could not mount Drive: {e}")
        return False


def _cache_filename(url):
    """Derive a stable cache filename from a download URL."""
    parsed = urllib.parse.urlparse(url)
    return os.path.basename(parsed.path)


def _try_load_from_cache(url, target_dir):
    """
    Check if a model exists in the Google Drive cache.
    If found, copy it to the target directory (fast local copy).

    @param {str} url — Model download URL
    @param {str} target_dir — ComfyUI model directory
    @returns {bool} True if cache hit and copied, False on miss
    """
    filename = _cache_filename(url)
    cache_path = os.path.join(DRIVE_CACHE_DIR, filename)
    dest_path = os.path.join(target_dir, filename)

    if os.path.isfile(cache_path):
        log.info(f"   💾 Drive cache hit: {filename[:40]}")
        os.makedirs(target_dir, exist_ok=True)
        shutil.copy2(cache_path, dest_path)
        log.success(f"   Copied from Drive cache")
        return True
    return False


def _save_to_cache(url, source_dir):
    """
    Copy a downloaded model file to the Google Drive cache for future runs.
    Creates the cache directory if needed.

    @param {str} url — Model download URL (used to derive filename)
    @param {str} source_dir — Directory where the file was downloaded
    @returns {None}
    """
    filename = _cache_filename(url)
    source_path = os.path.join(source_dir, filename)
    cache_path = os.path.join(DRIVE_CACHE_DIR, filename)

    if not os.path.isfile(source_path):
        return

    os.makedirs(DRIVE_CACHE_DIR, exist_ok=True)
    try:
        log.info(f"   📤 Saving to Drive cache: {filename[:40]}...")
        shutil.copy2(source_path, cache_path)
        log.success("   Cached to Drive for next session")
    except Exception as e:
        log.warn(f"   Could not cache to Drive: {e}")


# ---- FEATURE: aria2c installer ----
# Notebook: run_quiet("apt -y install -qq aria2", "Installing Accelerator (Aria2)")

def ensure_aria2():
    """
    Install aria2c if not already present on the system.
    Called once during initialization to guarantee availability.

    Matches notebook: run_quiet("apt -y install -qq aria2", "Installing Accelerator (Aria2)")

    @returns {None}
    """
    try:
        subprocess.run(
            ["aria2c", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        subprocess.run(
            ["apt-get", "-y", "install", "-qq", "aria2"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        log.info("aria2c installed successfully")


# ══════════════════════════════════════════════════════════════
# DOWNLOAD ENGINE
# ══════════════════════════════════════════════════════════════

# ---- FEATURE: Single file downloader ----
# Notebook: run_quiet(f"aria2c --console-log-level=error -c -x 16 -s 16 -k 1M '{url}' -d '{path.parent}' -o '{path.name}'", ...)

def download_file(url, target_dir, use_drive_cache=True):
    """
    Download a single file to the target directory.
    Automatically detects Google Drive, Civitai, and direct URLs.
    Checks Google Drive cache first — if cached, copies locally (fast).
    After download, saves a copy to Drive cache for future sessions.

    Matches notebook's aria2c flags: --console-log-level=error -c -x 16 -s 16 -k 1M

    @param {str} url — Full download URL
    @param {str} target_dir — Local directory to save into
    @param {bool} use_drive_cache — Whether to check/save Drive cache (default True)
    @returns {None}
    """
    os.makedirs(target_dir, exist_ok=True)

    # ─── Try Drive cache first ───
    if use_drive_cache and "drive.google.com" not in url:
        if _try_load_from_cache(url, target_dir):
            return

    before = set(os.listdir(target_dir))

    try:
        # ─── Google Drive (gdown) ───
        if "drive.google.com" in url:
            if gdown is None:
                raise ImportError("gdown is required for Google Drive downloads")
            log.info("   📥 Downloading from Drive...")
            gdown.download(url, output=target_dir + "/", quiet=False, fuzzy=True)

        # ─── Direct / Civitai / HuggingFace ───
        else:
            parsed = urllib.parse.urlparse(url)
            filename = os.path.basename(parsed.path)
            log.info(f"   📥 Fetching: {filename[:40]}...")

            # Notebook exact flags: aria2c --console-log-level=error -c -x 16 -s 16 -k 1M
            cmd = [
                "aria2c",
                "--console-log-level=error",
                "--summary-interval=10",
                "-c", "-x", "16", "-s", "16", "-k", "1M",
            ]

            if "civitai.com" in url:
                cmd.extend(["--content-disposition", url, "-d", target_dir])
            elif filename:
                cmd.extend(["-o", filename, url, "-d", target_dir])
            else:
                cmd.extend(["--content-disposition", url, "-d", target_dir])

            subprocess.run(cmd, check=True)

        # ─── Report new files ───
        after = set(os.listdir(target_dir))
        new = after - before
        if new:
            log.success(f"   Saved as: {list(new)[0]}")
        else:
            log.success("   Download complete")

        # ─── Save to Drive cache for next session ───
        if use_drive_cache and "drive.google.com" not in url:
            _save_to_cache(url, target_dir)

    except Exception as e:
        log.error(f"   Failed: {url}\n      Error: {e}\n")


# ---- FEATURE: Batch download processor ----

def process_downloads(urls, target_dir):
    """
    Parse a comma or newline-separated URL string and download each.
    Skips empty lines and whitespace-only entries gracefully.

    @param {str} urls — Raw URL string (comma/newline separated)
    @param {str} target_dir — Local directory to save all files
    @returns {None}
    """
    if not urls.strip():
        return

    url_list = [u.strip() for u in urls.replace(",", "\n").split("\n") if u.strip()]
    os.makedirs(target_dir, exist_ok=True)
    log.info(f"\n📂 Directory: {os.path.basename(target_dir)}")

    for url in url_list:
        download_file(url, target_dir)


# ══════════════════════════════════════════════════════════════
# EXPORTS
# ══════════════════════════════════════════════════════════════

__all__ = ["ensure_aria2", "mount_drive", "download_file", "process_downloads"]

# ══════════════════════════════════════════════════════════════ END: downloader.py
