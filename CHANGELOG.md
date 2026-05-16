# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
