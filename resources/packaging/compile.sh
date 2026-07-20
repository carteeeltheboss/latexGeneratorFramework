#!/usr/bin/env sh
set -eu

COMPILER="${LATEX_COMPILER:-pdflatex}"

if ! command -v latexmk >/dev/null 2>&1; then
  echo "Error: latexmk was not found in PATH." >&2
  echo "Install and configure a LaTeX distribution before running this script." >&2
  exit 1
fi

if ! command -v "$COMPILER" >/dev/null 2>&1; then
  echo "Error: $COMPILER was not found in PATH." >&2
  exit 1
fi

case "$COMPILER" in
  pdflatex) MODE="-pdf" ;;
  lualatex) MODE="-lualatex" ;;
  xelatex) MODE="-xelatex" ;;
  *) echo "Unsupported LATEX_COMPILER: $COMPILER" >&2; exit 1 ;;
esac

latexmk "$MODE" -interaction=nonstopmode -halt-on-error main.tex
