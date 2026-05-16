# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.1.3] - 2026-05-16

### Changed
- `README.md` — Kaggle Quick Start now has step-by-step import instructions with raw GitHub URL for File → Import Notebook
- `GUIDE.md` — Kaggle Getting Started updated with clear 3-step import flow and raw URL
- `src/__init__.py` — version bump to 1.1.3

---

## [1.1.2] - 2026-05-16

### Changed
- `README.md` — replaced all Colab-only references with platform-agnostic language (Colab + Kaggle): tags, overview, features table, project structure, resource requirements, FAQ, troubleshooting
- `src/__init__.py` — version bump to 1.1.2

---

## [1.1.1] - 2026-05-16

### Changed
- `GUIDE.md` — updated for dual-platform support: added Kaggle setup instructions alongside Colab, platform-specific file paths for both environments, Kaggle troubleshooting entries (No GPU, No Internet, file download location)
- `src/__init__.py` — version bump to 1.1.1

---

## [1.1.0] - 2026-05-16

### Added
- `notebook/ZImagePro-Kaggle.ipynb` — Kaggle Notebook variant with Kaggle-specific paths, GPU/Internet setup instructions, and Kaggle sidebar download guidance
- `src/config.py` — platform auto-detection (`PLATFORM`): detects Colab, Kaggle, or local environment and sets paths accordingly (`WORKSPACE`, `RESULTS_DIR`)
- README.md — Kaggle badge, Kaggle Quick Start section, Kaggle troubleshooting entries
- Colab notebook footer — added Kaggle badge link

### Changed
- `src/config.py` — `WORKSPACE` is now dynamically resolved per platform (`/content/ComfyUI`, `/kaggle/working/ComfyUI`, or local)
- `src/generator.py` — uses platform-aware `RESULTS_DIR` from config instead of hardcoded `/content/results`
- `src/exporter.py` — `zip_outputs()` and `download_zip()` now auto-detect platform paths; `download_zip()` shows Kaggle-specific download instructions on Kaggle
- `src/__init__.py` — version bump to 1.1.0

---

## [1.0.5] - 2026-05-16

### Fixed
- `src/generator.py` — added `_check_cuda()` pre-flight validation before importing ComfyUI nodes; raises `RuntimeError` with clear fix instructions instead of cryptic `AssertionError: Torch not compiled with CUDA enabled`
- `notebook/ZImagePro.ipynb` — Cell 1 now detects CUDA availability before dependency install and auto-installs CUDA-enabled PyTorch (`cu121`) if missing, with GPU runtime instructions if detection still fails
- `requirements.txt` — added `numpy<2` pin to prevent ComfyUI compatibility issues with numpy 2.x

### Changed
- `src/__init__.py` — version bump to 1.0.5

---

## [1.0.4] - 2026-05-16

### Added
- Content Safety Notice markdown cell in notebook (between Initialize and Generate steps)
- Warning about unfiltered model, prohibited uses, and HuggingFace content policy

### Changed
- `GUIDE.md` — complete rewrite matching ZImageLora style: beginner explanations, expandable FAQ, detailed step walkthroughs, all settings tables, resolution guide, sampler guide, prompt writing tips, file locations, troubleshooting with causes/fixes, content safety notice, footer with badges

---

## [1.0.3] - 2026-05-16

### Fixed
- `src/config.py` — added missing `__all__` export declaration
- `src/__init__.py` — added missing `__all__` export declaration
- `GUIDE.md` — added "Creator Studio" cell reference (matches notebook Cell 3 name)
- Removed stray `__pycache__` artifacts

---

## [1.0.2] - 2026-05-16

### Added
- `GUIDE.md` — comprehensive beginner-friendly user guide (Colab setup, settings, prompting, FAQ)
- `PROMPT.md` — 8 ready-to-use example prompts with full settings
- `CONTRIBUTING.md` — contribution guidelines (bugs, features, code style, commit format)

### Changed
- `src/__init__.py` — now exports shared colored UI logger (`log`) and `run_quiet()` helper matching notebook style
- All `src/` modules — use shared `log` from `__init__.py` instead of per-module logger classes
- `src/generator.py` — added notebook-matching colored output (`Booting ComfyUI Backend...`, `Engine Online.`)
- `src/downloader.py` — uses shared logger for consistent colored output
- `src/exporter.py` — uses shared logger for consistent colored output
- `README.md` — updated project structure and What's Included table with new files

---

## [1.0.1] - 2026-05-16

### Fixed
- `src/generator.py` — seed generation now uses `torch.randint` (matching original notebook) instead of Python `random.randint`

---

## [1.0.0] - 2026-05-16

### Added
- Initial release of Z-Image Turbo Pro
- Modular `src/` package with separated concerns: config, downloader, generator, exporter
- `src/config.py` — all constants, model URLs, defaults, resolution presets, sampler/scheduler lists
- `src/downloader.py` — aria2c-powered asset downloader with 16-parallel connections, Google Drive & Civitai support
- `src/generator.py` — in-process ComfyUI node loading and image generation (FP8 optimized)
- `src/exporter.py` — zip output and Colab browser download helper
- `notebook/ZImagePro.ipynb` — 3-cell Colab notebook using modular src/ imports
- `README.md` — comprehensive documentation with architecture diagrams, parameter tables, FAQ, troubleshooting
- `CHANGELOG.md` — version history tracking
- `SECURITY.md` — vulnerability reporting policy
- `.github/ISSUE_TEMPLATE/` — bug report and feature request templates
- `.github/PULL_REQUEST_TEMPLATE.md` — PR checklist
- `.gitignore` — Python, Jupyter, model files, OS artifacts
- `requirements.txt` — core ML and ComfyUI dependencies
- `LICENSE` — MIT license

### Changed
- Refactored monolithic notebook cells into clean modular `src/` package
- Replaced inline model URLs with centralized `config.py` constants
- Replaced inline download logic with reusable `downloader.py` module
- Replaced inline generation logic with reusable `generator.py` module
- Replaced inline export logic with reusable `exporter.py` module
- Updated notebook badges to point to standalone ZImagePro repository
- Updated footer links to reference ZImagePro repo instead of Notebooks repo
