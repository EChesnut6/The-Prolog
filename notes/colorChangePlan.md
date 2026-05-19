# Implementation Plan: The Cinematic Primer

A zero-cost, static site generator designed to provide spoiler-free "pre-viewing context," technical production footprints, and dynamic thematic vibes for movie nights with friends.

---

## 🛠️ Architecture Overview

- **Frontend:** Semantic HTML5, Custom CSS3 (with dynamic CSS variables), hosted for free on **GitHub Pages**.
- **Backend (Local Engine):** Python 3 script that parses raw text drafts, requests structural metadata from the **TMDB API**, extracts palette data from poster assets, and compiles production-ready HTML files.
- **Security Guardrail:** The TMDB API Key remains strictly stored in a local `.env` file, ensuring zero public exposure on the client side.

---

## 🚀 Step-by-Step Execution Roadmap

### Phase 1: Local Workspace & API Setup
- [ ] Create a public GitHub repository named `[your-username].github.io` (or a specific project name repository).
- [ ] Register for a free Developer API Key on [The Movie Database (TMDB)](https://www.themoviedb.org/).
- [ ] Initialize your local directory with the following structural footprint:
  ```text
  ├── generator.py
  ├── template.html
  ├── .env
  ├── .gitignore
  ├── assets/
  │   └── references/      # Local files for visual influences (e.g., hypnosis.jpg)
  └── reviews/             # Target directory for generated review pages