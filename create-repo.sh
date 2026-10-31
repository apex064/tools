#!/usr/bin/env bash
set -Eeuo pipefail

# Create a GitHub repository from the current directory and push its contents.
# Usage: ./create-repo.sh [repo-name] [public|private]

usage() {
  cat <<'EOF'
Usage:
  create-repo.sh [repository-name] [public|private]

Examples:
  create-repo.sh tools public
  create-repo.sh my-project private
  create-repo.sh                 # prompts for both values

Run this script from the project folder you want to publish.
EOF
}

die() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

command -v git >/dev/null 2>&1 || die "Git is not installed."
command -v gh  >/dev/null 2>&1 || die "GitHub CLI (gh) is not installed. Install it first."

if ! gh auth status >/dev/null 2>&1; then
  die "GitHub CLI is not authenticated. Run: gh auth login"
fi

repo_name="${1:-}"
visibility="${2:-}"

if [[ -z "$repo_name" ]]; then
  read -r -p "GitHub repository name: " repo_name
fi

if [[ -z "$repo_name" ]]; then
  die "Repository name cannot be empty."
fi

if [[ -z "$visibility" ]]; then
  read -r -p "Visibility (public/private): " visibility
fi

visibility="${visibility,,}"
case "$visibility" in
  public|private) ;;
  *) die "Visibility must be either 'public' or 'private'." ;;
esac

# Avoid accidentally publishing a parent directory's contents.
if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  git init
fi

repo_root="$(git rev-parse --show-toplevel)"
current_dir="$(pwd -P)"
repo_root="$(cd "$repo_root" && pwd -P)"

if [[ "$current_dir" != "$repo_root" ]]; then
  printf 'Note: Git repository root is %s\n' "$repo_root"
  printf 'The script will publish the Git repository root, not just the current subfolder.\n'
fi

cd "$repo_root"

# Use main as the default branch.
git branch -M main

# Refuse to silently replace an existing remote.
if git remote get-url origin >/dev/null 2>&1; then
  existing_origin="$(git remote get-url origin)"
  printf 'An origin remote already exists: %s\n' "$existing_origin"
  read -r -p "Replace origin with the new GitHub repository? [y/N] " answer
  case "${answer,,}" in
    y|yes) ;;
    *) die "Cancelled. Existing origin was left unchanged." ;;
  esac
fi

# Stage all project files (respecting .gitignore).
git add -A

# Create an initial commit if needed, or commit pending changes.
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  if git diff --cached --quiet; then
    die "There are no files to commit. Add project files and try again."
  fi
  git commit -m "Initial commit"
elif ! git diff --cached --quiet || ! git diff --quiet || [[ -n "$(git ls-files --others --exclude-standard)" ]]; then
  git commit -m "Update project"
fi

# Create the GitHub repository, configure origin, and push.
if git remote get-url origin >/dev/null 2>&1; then
  git remote remove origin
fi

gh repo create "$repo_name" "--$visibility" --source=. --remote=origin
git push -u origin main

printf '\nSuccess! Repository created and pushed:\n'
gh repo view --web
