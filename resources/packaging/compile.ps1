$ErrorActionPreference = "Stop"
$Compiler = if ($env:LATEX_COMPILER) { $env:LATEX_COMPILER } else { "pdflatex" }

if (-not (Get-Command latexmk -ErrorAction SilentlyContinue)) {
    Write-Error "latexmk was not found in PATH. Install and configure a LaTeX distribution first."
    exit 1
}
if (-not (Get-Command $Compiler -ErrorAction SilentlyContinue)) {
    Write-Error "$Compiler was not found in PATH."
    exit 1
}

$Mode = switch ($Compiler) {
    "pdflatex" { "-pdf" }
    "lualatex" { "-lualatex" }
    "xelatex" { "-xelatex" }
    default { Write-Error "Unsupported LATEX_COMPILER: $Compiler"; exit 1 }
}

& latexmk $Mode -interaction=nonstopmode -halt-on-error main.tex
exit $LASTEXITCODE
