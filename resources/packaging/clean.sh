#!/usr/bin/env sh
set -eu
if command -v latexmk >/dev/null 2>&1; then
  latexmk -C main.tex
else
  rm -f -- *.aux *.bbl *.bcf *.blg *.fdb_latexmk *.fls *.lof *.log *.nav *.out *.run.xml *.snm *.toc *.vrb
fi
