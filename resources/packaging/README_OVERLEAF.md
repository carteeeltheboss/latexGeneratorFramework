# Overleaf compilation

This package contains a temporary `main.tex` wrapper. First send `generation_prompt.txt`, `presentation_template.tex`, and the `assets/` folder to the AI. Replace `main.tex` with the complete file returned by the AI.

1. Keep `main.tex` at the ZIP root.
2. In Overleaf, choose **New Project → Upload Project**.
3. Upload the ZIP.
4. Set **Main document** to `main.tex`.
5. Select the compiler requested in the generated prompt.
6. Click **Recompile**.
7. When an asset is missing, add it at the exact relative path shown in the error.

No local LaTeX installation is required.
