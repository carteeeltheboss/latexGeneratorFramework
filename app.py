from __future__ import annotations

import io
import os
import tempfile
import time
import uuid
import zipfile
from pathlib import Path
from typing import Any

import yaml
from flask import Flask, abort, render_template, request, send_file
from jinja2 import Environment, StrictUndefined
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = BASE_DIR / "resources"
EXPORT_DIR = Path(tempfile.gettempdir()) / "agentic-presentation-builder"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}
EXPORT_TTL_SECONDS = 60 * 60

app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=25 * 1024 * 1024,
    SECRET_KEY=os.environ.get("SECRET_KEY", "local-only-development-key"),
)


def text(name: str, default: str = "") -> str:
    return request.form.get(name, default).strip()


def first_text(*names: str, default: str = "") -> str:
    """Return the first non-empty form value from compatible field aliases."""
    for name in names:
        value = request.form.get(name)
        if value is not None and value.strip():
            return value.strip()
    return default.strip()


def lines(name: str) -> list[str]:
    return [line.strip(" -\t") for line in text(name).splitlines() if line.strip(" -\t")]


def tri_state(name: str, default: str = "auto") -> str:
    value = text(name, default).lower()
    return value if value in {"yes", "no", "auto"} else default


def boolean(name: str) -> bool:
    return request.form.get(name) in {"on", "true", "1", "yes"}


def integer(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(text(name, str(default)))
    except ValueError:
        return default
    return max(minimum, min(maximum, value))


def clean_old_exports() -> None:
    now = time.time()
    for path in EXPORT_DIR.glob("*.zip"):
        try:
            if now - path.stat().st_mtime > EXPORT_TTL_SECONDS:
                path.unlink(missing_ok=True)
                path.with_suffix(".name").unlink(missing_ok=True)
        except OSError:
            continue


def read_resource(relative_path: str) -> str:
    return (RESOURCES_DIR / relative_path).read_text(encoding="utf-8")


def uploaded_assets() -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for storage in request.files.getlist("project_assets"):
        if not storage or not storage.filename:
            continue
        safe_name = secure_filename(storage.filename)
        suffix = Path(safe_name).suffix.lower()
        if suffix not in ALLOWED_ASSET_EXTENSIONS:
            continue
        data = storage.read()
        if not data:
            continue
        assets.append(
            {
                "filename": safe_name,
                "archive_path": f"assets/user/{safe_name}",
                "data": data,
            }
        )
    return assets


def uploaded_partner_logo() -> dict[str, Any] | None:
    storage = request.files.get("partner_logo")
    if not storage or not storage.filename:
        return None
    safe_name = secure_filename(storage.filename)
    suffix = Path(safe_name).suffix.lower()
    if suffix not in ALLOWED_ASSET_EXTENSIONS:
        return None
    data = storage.read()
    if not data:
        return None
    archive_path = f"assets/logos/partner-logo{suffix}"
    return {"filename": safe_name, "archive_path": archive_path, "data": data}


def build_configuration(partner_logo: dict[str, Any] | None, assets: list[dict[str, Any]]) -> dict[str, Any]:
    presentation_type = text("presentation_type", "school_project")
    organisation_enabled = presentation_type == "internship" or boolean("organisation_enabled")

    return {
        "presentation": {
            "type": presentation_type,
            "title": text("title"),
            "subtitle": text("subtitle"),
            "language": text("language", "english"),
            "duration_minutes": integer("duration_minutes", 15, 3, 120),
            "target_slide_count": integer("target_slide_count", 16, 5, 80),
            "audience": text("audience", "academic jury"),
            "tone": text("tone", "professional and technical"),
        },
        "identity": {
            "presenters": lines("presenters"),
            "academic_supervisor": text("academic_supervisor"),
            "email": text("email"),
            "presentation_date": text("presentation_date"),
            "location": text("location"),
            "academic_year": text("academic_year"),
            "programme": text("programme"),
            "institution": "EMSI",
            "institution_logo": "assets/logos/emsi-logo.png",
        },
        "organisation": {
            "enabled": organisation_enabled,
            "name": first_text("organisation_name", "organization_name", "partner_name", "company_name") if organisation_enabled else "",
            "department": text("organisation_department") if organisation_enabled else "",
            "supervisor": text("organisation_supervisor") if organisation_enabled else "",
            "logo": partner_logo["archive_path"] if organisation_enabled and partner_logo else "",
        },
        "project": {
            "context": text("context"),
            "problem": text("problem"),
            "proposed_solution": text("proposed_solution"),
            "objectives": lines("objectives"),
            "technologies": lines("technologies"),
            "requirements": lines("requirements"),
            "implementation_highlights": lines("implementation_highlights"),
            "testing": lines("testing"),
            "results": lines("results"),
            "challenges": lines("challenges"),
            "future_work": lines("future_work"),
            "repository_url": text("repository_url"),
        },
        "planning": {
            "methodology": text("methodology", "auto"),
            "task_table": tri_state("task_table"),
            "pert": tri_state("pert"),
            "gantt": tri_state("gantt"),
            "critical_path": tri_state("critical_path"),
            "tasks_and_dependencies": lines("tasks_and_dependencies"),
        },
        "visuals": {
            "tikz_intensity": text("tikz_intensity", "high"),
            "text_density": text("text_density", "low"),
            "architecture_diagram": tri_state("architecture_diagram"),
            "workflow_diagram": tri_state("workflow_diagram"),
            "use_case_diagram": tri_state("use_case_diagram"),
            "sequence_diagram": tri_state("sequence_diagram"),
            "data_model_diagram": tri_state("data_model_diagram"),
            "deployment_diagram": tri_state("deployment_diagram"),
            "screenshots": tri_state("screenshots"),
            "uploaded_assets": [asset["archive_path"] for asset in assets],
        },
        "output": {
            "target": text("output_target", "overleaf"),
            "compiler": text("compiler", "pdflatex"),
            "bibliography": text("bibliography", "none"),
            "shell_escape": boolean("shell_escape"),
            "main_file": "main.tex",
        },
    }


def validate_configuration(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not config["presentation"]["title"]:
        errors.append("Presentation title is required.")
    if not config["identity"]["presenters"]:
        errors.append("At least one presenter is required.")
    if not config["project"]["problem"]:
        errors.append("A problem statement is required.")
    if config["organisation"]["enabled"] and not config["organisation"]["name"]:
        errors.append("Organisation name is required when organisation context is enabled.")
    return errors


def render_generation_prompt(config: dict[str, Any]) -> tuple[str, str]:
    project_yaml = yaml.safe_dump(
        config,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=100,
    )
    environment = Environment(undefined=StrictUndefined, autoescape=False)
    template = environment.from_string(read_resource("prompt_template.md"))
    prompt = template.render(
        project_yaml=project_yaml,
        output_target=config["output"]["target"],
        compiler=config["output"]["compiler"],
        main_file=config["output"]["main_file"],
    )
    return prompt, project_yaml


def wrapper_main_tex() -> str:
    return r"""% Temporary wrapper. Replace this file with the AI-generated main.tex.
% It compiles the reusable template so the package can be checked immediately.
\input{presentation_template.tex}
"""


def add_common_generation_files(
    archive: zipfile.ZipFile,
    prompt: str,
    partner_logo: dict[str, Any] | None,
    assets: list[dict[str, Any]],
) -> None:
    archive.writestr("presentation_template.tex", read_resource("presentation_template.tex"))
    archive.writestr("generation_prompt.txt", prompt)
    archive.writestr("main.tex", wrapper_main_tex())
    archive.writestr("assets/logos/README.md", read_resource("assets/logos/README.md"))
    archive.writestr("assets/images/README.md", read_resource("assets/images/README.md"))
    if partner_logo:
        archive.writestr(partner_logo["archive_path"], partner_logo["data"])
    for asset in assets:
        archive.writestr(asset["archive_path"], asset["data"])


def add_overleaf_files(archive: zipfile.ZipFile) -> None:
    archive.writestr("README_OVERLEAF.md", read_resource("packaging/README_OVERLEAF.md"))


def add_local_files(archive: zipfile.ZipFile, compiler: str = "pdflatex") -> None:
    shell_script = read_resource("packaging/compile.sh").replace(
        "${LATEX_COMPILER:-pdflatex}", f"${{LATEX_COMPILER:-{compiler}}}"
    )
    powershell_script = read_resource("packaging/compile.ps1").replace(
        'else { "pdflatex" }', f'else {{ "{compiler}" }}'
    )
    archive.writestr("README_LOCAL.md", read_resource("packaging/README_LOCAL.md"))
    archive.writestr("latexmkrc", read_resource("packaging/latexmkrc"))
    archive.writestr("compile.sh", shell_script)
    archive.writestr("compile.ps1", powershell_script)
    archive.writestr("clean.sh", read_resource("packaging/clean.sh"))
    archive.writestr("clean.ps1", read_resource("packaging/clean.ps1"))


def build_generation_zip(
    config: dict[str, Any],
    prompt: str,
    partner_logo: dict[str, Any] | None,
    assets: list[dict[str, Any]],
) -> bytes:
    target = config["output"]["target"]
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w", zipfile.ZIP_DEFLATED) as archive:
        if target == "both":
            for folder, local_target in (("overleaf", "overleaf"), ("local", "local")):
                nested = io.BytesIO()
                with zipfile.ZipFile(nested, "w", zipfile.ZIP_DEFLATED) as nested_archive:
                    add_common_generation_files(nested_archive, prompt, partner_logo, assets)
                    if local_target == "overleaf":
                        add_overleaf_files(nested_archive)
                    else:
                        add_local_files(nested_archive, config["output"]["compiler"])
                nested.seek(0)
                with zipfile.ZipFile(nested, "r") as nested_archive:
                    for name in nested_archive.namelist():
                        archive.writestr(f"{folder}/{name}", nested_archive.read(name))
            archive.writestr("README.md", read_resource("packaging/README_BOTH.md"))
        else:
            add_common_generation_files(archive, prompt, partner_logo, assets)
            if target == "local":
                add_local_files(archive, config["output"]["compiler"])
            else:
                add_overleaf_files(archive)
    return memory.getvalue()


def safe_output_name(title: str, suffix: str = "generation-package.zip") -> str:
    stem = secure_filename(title.lower().replace(" ", "-")) or "presentation"
    return f"{stem}-{suffix}"


def store_export(data: bytes, filename: str) -> str:
    clean_old_exports()
    token = uuid.uuid4().hex
    path = EXPORT_DIR / f"{token}.zip"
    path.write_bytes(data)
    (EXPORT_DIR / f"{token}.name").write_text(filename, encoding="utf-8")
    return token


def build_final_package(main_tex: str, target: str, compiler: str, assets: list[dict[str, Any]]) -> bytes:
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("main.tex", main_tex)
        archive.writestr("assets/logos/README.md", read_resource("assets/logos/README.md"))
        archive.writestr("assets/images/README.md", read_resource("assets/images/README.md"))
        for asset in assets:
            archive.writestr(asset["archive_path"], asset["data"])
        if target == "local":
            add_local_files(archive, compiler)
        else:
            add_overleaf_files(archive)
    return memory.getvalue()


@app.get("/")
def index():
    return render_template("index.html", previous={}, initial_step=1)


@app.post("/generate")
def generate():
    partner_logo = uploaded_partner_logo()
    assets = uploaded_assets()
    config = build_configuration(partner_logo, assets)
    errors = validate_configuration(config)
    if errors:
        initial_step = 2 if any("Organisation name" in error for error in errors) else 1
        return render_template(
            "index.html",
            errors=errors,
            previous=request.form.to_dict(flat=True),
            initial_step=initial_step,
        ), 400

    prompt, project_yaml = render_generation_prompt(config)
    data = build_generation_zip(config, prompt, partner_logo, assets)
    filename = safe_output_name(config["presentation"]["title"])
    token = store_export(data, filename)

    return render_template(
        "result.html",
        token=token,
        filename=filename,
        config=config,
        project_yaml=project_yaml,
        prompt_preview=prompt[:5000],
    )


@app.get("/download/<token>")
def download(token: str):
    if not token.isalnum() or len(token) != 32:
        abort(404)
    path = EXPORT_DIR / f"{token}.zip"
    name_path = EXPORT_DIR / f"{token}.name"
    if not path.exists():
        abort(404)
    filename = name_path.read_text(encoding="utf-8") if name_path.exists() else "presentation-package.zip"
    return send_file(path, as_attachment=True, download_name=filename, mimetype="application/zip")


@app.post("/package-generated")
def package_generated():
    target = text("package_target", "overleaf")
    if target not in {"overleaf", "local"}:
        target = "overleaf"

    main_tex = text("main_tex")
    main_file = request.files.get("main_tex_file")
    if main_file and main_file.filename:
        main_tex = main_file.read().decode("utf-8", errors="replace")
    if "\\documentclass" not in main_tex or "\\begin{document}" not in main_tex:
        return render_template(
            "package_error.html",
            message="The supplied file does not look like a complete LaTeX presentation.",
        ), 400

    compiler = text("package_compiler", "pdflatex")
    if compiler not in {"pdflatex", "lualatex", "xelatex"}:
        compiler = "pdflatex"
    assets = uploaded_assets()
    data = build_final_package(main_tex, target, compiler, assets)
    return send_file(
        io.BytesIO(data),
        as_attachment=True,
        download_name=f"presentation-{target}.zip",
        mimetype="application/zip",
    )


@app.errorhandler(413)
def too_large(_error):
    return render_template(
        "package_error.html",
        message="The upload is too large. Keep the complete request under 25 MB.",
    ), 413


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5500"))
    app.run(host=host, port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
