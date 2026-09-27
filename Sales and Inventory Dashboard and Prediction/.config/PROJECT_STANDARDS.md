# Project Standards & Git Workflow

This document outlines the standard operating procedures for the Sales & Inventory Forecasting project. Both the developer and the AI assistant (Antigravity) must strictly adhere to these rules.

## 1. Branching Strategy
We follow a structured feature-branch workflow to keep the main codebase stable.
- `main` : Stable, production-ready code. Never push directly to `main` without testing.
- `feature/<name>` : For new features (e.g., `feature/eda-setup`, `feature/prophet-model`).
- `fix/<name>` : For bug fixes (e.g., `fix/data-cleaning-bug`).
- `docs/<name>` : For documentation updates.

## 2. Commit Message Convention
We use [Conventional Commits](https://www.conventionalcommits.org/). Every commit message must be clear and descriptive.
Format: `<type>: <description>`
- `feat:` A new feature or script (e.g., `feat: add initial EDA notebook`).
- `fix:` A bug fix (e.g., `fix: resolve division by zero in forecast logic`).
- `docs:` Documentation changes only.
- `style:` Formatting, missing semi-colons, etc. (no code logic changes).
- `refactor:` Code changes that neither fix a bug nor add a feature.
- `chore:` Updating build tasks, package manager configs, or docker files.

## 3. Git Push & Pull Workflow
1. **Sync:** Always pull the latest changes before starting new work: `git pull origin main`
2. **Branch:** Create a new branch for your task: `git checkout -b feature/my-feature`
3. **Stage:** Review your changes and stage them: `git add <files>`
4. **Commit:** `git commit -m "feat: update something"`
5. **Push:** `git push -u origin feature/my-feature`
6. **Merge:** Review the code via Pull Request (or merge locally), then integrate into `main`.

## 4. Rules for AI (Antigravity)
- **No blind commits:** The AI must outline the proposed commits and ask the user before running `git commit`.
- **Atomic commits:** Keep commits small, logical, and focused on a single task.
- **Check status:** Always run `git status` and `git diff` before committing to verify exactly what is being staged.
- **Never force push:** Do not use `git push -f` unless explicitly commanded by the user.
- **Strictly follow Conventional Commits:** All automated commits must start with the correct prefix (`feat:`, `fix:`, `chore:`, etc.).

## 5. Coding Standards
- Write clean, documented Python code.
- Ensure all FastAPI endpoints are typed using Pydantic.
- Place exploratory work in Jupyter Notebooks (`.ipynb`), but move final production code to Python modules (`.py`).
