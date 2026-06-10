#!/usr/bin/env bash
# Install the AcademiCats skill family into Claude Code (~/.claude/skills/).
# Safe to re-run: it updates any skill already installed.
set -e

DIR="${HOME}/.claude/skills"
mkdir -p "$DIR"

install_skill () {   # $1 = repo name   $2 = skill folder
  if [ -d "$DIR/$2/.git" ]; then
    echo "↻ updating $2"
    git -C "$DIR/$2" pull --ff-only --quiet || true
  else
    echo "↓ installing $2"
    git clone --depth 1 --quiet "https://github.com/academicatstool-netizen/$1.git" "$DIR/$2"
  fi
}

install_skill Cat_paper_search  paper-search
install_skill Cat_synthesis_lab synthesis-lab
install_skill Cat_paper_review  paper-review

echo "↓ installing pypdf (needed by Paper Search deep read)"
python -m pip install --quiet pypdf 2>/dev/null \
  || python3 -m pip install --quiet pypdf 2>/dev/null \
  || echo "  ⚠ couldn't auto-install pypdf — run: pip install pypdf"

echo ""
echo "✅ AcademiCats skills installed in $DIR"
echo "   Restart Claude Code to load them, then just ask — e.g. \"find recent papers on …\"."
