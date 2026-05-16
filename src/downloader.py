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
import subprocess
import urllib.parse

try:
    import gdown
except ImportError:
    gdown = None

from . import log

# ══════════════════════════════════════════════════════════════
# ENVIRONMENT SETUP
# ══════════════════════════════════════════════════════════════

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

def download_file(url, target_dir):
    """
    Download a single file to the target directory.
    Automatically detects Google Drive, Civitai, and direct URLs.

    Matches notebook's aria2c flags: --console-log-level=error -c -x 16 -s 16 -k 1M

    @param {str} url — Full download URL
    @param {str} target_dir — Local directory to save into
    @returns {None}
    """
    os.makedirs(target_dir, exist_ok=True)
    before = set(os.listdir(target_dir))

    try:
        # ─── Google Drive ───
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

__all__ = ["ensure_aria2", "download_file", "process_downloads"]

# ══════════════════════════════════════════════════════════════ END: downloader.py
