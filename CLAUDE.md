# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Mintlify documentation site for the **Trassets Data API** (a read-only REST API over real-estate data synced into RDS PostgreSQL). No application code — this repo is entirely MDX content plus `docs.json` navigation/theme config.

## Commands

```bash
npm i -g mint      # install the Mintlify CLI (once)
mint dev            # local preview at http://localhost:3000, run from repo root (where docs.json lives)
mint update          # fix a dev server that won't start / stale CLI
```

No build, lint, or test step. Changes deploy automatically on push to the default branch (GitHub app connected to the Mintlify dashboard). A page 404s locally only if `mint dev` isn't run from the folder containing `docs.json`.

## Structure

- `docs.json` — single source of truth for navigation, theme, logo, navbar links. Has a **top-level `navigation.languages` array** with two entries: `en` (default) and `de`. Each language has its own `tabs` → `groups` → `pages` tree — adding a page requires registering it in `docs.json` under the correct language, or it won't appear in the sidebar.
- English content lives at repo root (`quickstart.mdx`, `concepts/*.mdx`, `data-model/*.mdx`, `guides/*.mdx`, `api-reference/introduction.mdx`).
- German content is a parallel tree under `de/`, mirroring the English paths 1:1 (`de/quickstart.mdx`, `de/concepts/*.mdx`, etc.). Keep both trees in sync — a new/changed English page usually needs the same treatment in `de/`.
- `api-reference/introduction.mdx` (and its `de/` counterpart) is hand-written; the actual endpoint pages are generated from the live OpenAPI spec at `https://api.trassets.ai/openapi.json`, referenced via an `"openapi"` key in a `docs.json` nav group rather than as MDX files. The generated endpoint pages themselves are not translated — the spec has one language.
- `.agents/skills/` — vendored Mintlify skills (`mintlify`, `mintlify-api`); consult these for component syntax and MDX conventions instead of guessing.
- `v1/data-model/AUTHORING.md` — framework/checklist for writing or editing pages under `v1/data-model/`, distilled from a documentation review. Read before creating or substantially editing a page there.

## Content conventions

- Frontmatter on every page: `title`, `sidebarTitle`, `description`. Match the existing phrasing style (`description` is a full sentence summarizing the page for search/AI surfaces).
- Field names, endpoint paths, and example payloads must reflect the **live** API — not aspirational/planned features. History here includes real incidents of invented fields and stale category names making it into docs (see `api-reference/introduction.mdx`'s note on the removed "Meters"/"Market Data" categories, and commit `f4f50af`); when documenting fields or endpoints, verify against `GET /catalog` or the OpenAPI spec rather than inferring from naming patterns.
- Cross-references use root-relative paths (e.g. `/data-model/field-glossary`); German pages link into `/de/...` equivalents.
- Commit messages are in German, often tagged with an Asana task ID (`Asana <gid>`) or PR number.
