$ErrorActionPreference = "Stop"
if (Get-Command latexmk -ErrorAction SilentlyContinue) {
    & latexmk -C main.tex
    exit $LASTEXITCODE
}
Get-ChildItem -File | Where-Object { $_.Extension -in ".aux", ".bbl", ".bcf", ".blg", ".fdb_latexmk", ".fls", ".lof", ".log", ".nav", ".out", ".run.xml", ".snm", ".toc", ".vrb" } | Remove-Item -Force
