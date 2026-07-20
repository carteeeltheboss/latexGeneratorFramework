# Local compilation

This package contains a temporary `main.tex` wrapper. First send `generation_prompt.txt`, `presentation_template.tex`, and the `assets/` folder to the AI. Replace `main.tex` with the complete file returned by the AI.

You are responsible for installing and configuring TeX Live or MiKTeX, `latexmk`, the selected compiler, and PATH.

## macOS / Linux

```bash
chmod +x compile.sh clean.sh
./compile.sh
```

## Windows PowerShell

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\compile.ps1
```

The scripts only detect tools and run compilation. They do not install dependencies or change PATH.
