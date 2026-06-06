"""Project scanner: discover files, detect language/category, count lines, sniff frameworks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .ignore import build_matcher

# extension -> language id
LANG_BY_EXT: dict[str, str] = {
    ".py": "python", ".pyi": "python",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript",
    ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php",
    ".java": "java", ".kt": "kotlin", ".kts": "kotlin", ".swift": "swift", ".scala": "scala",
    ".c": "c", ".h": "c", ".cc": "cpp", ".cpp": "cpp", ".cxx": "cpp", ".hpp": "cpp", ".hh": "cpp",
    ".cs": "csharp", ".lua": "lua", ".sh": "shell", ".bash": "shell", ".zsh": "shell",
    ".ps1": "powershell", ".psm1": "powershell",
    ".sql": "sql", ".graphql": "graphql", ".gql": "graphql", ".proto": "protobuf",
    ".html": "html", ".htm": "html", ".css": "css", ".scss": "css", ".sass": "css", ".less": "css",
    ".vue": "vue", ".svelte": "svelte",
    ".md": "markdown", ".markdown": "markdown", ".mdx": "markdown",
    ".rst": "restructuredtext", ".txt": "plaintext",
    ".json": "json", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml", ".ini": "ini",
    ".xml": "xml", ".csv": "csv", ".env": "env",
    ".tf": "terraform", ".tfvars": "terraform", ".hcl": "hcl",
    # --- Hardware description / legacy / scientific ---
    ".vhd": "vhdl", ".vhdl": "vhdl",
    ".v": "verilog", ".sv": "verilog", ".svh": "verilog", ".vh": "verilog",
    ".cob": "cobol", ".cbl": "cobol", ".cpy": "cobol",
    ".f": "fortran", ".for": "fortran", ".ftn": "fortran",
    ".f90": "fortran", ".f95": "fortran", ".f03": "fortran", ".f08": "fortran",
    ".adb": "ada", ".ads": "ada",
    ".pas": "pascal", ".pp": "pascal",
    # --- Functional / JVM / others ---
    ".hs": "haskell", ".lhs": "haskell",
    ".ml": "ocaml", ".mli": "ocaml",
    ".ex": "elixir", ".exs": "elixir",
    ".erl": "erlang", ".hrl": "erlang",
    ".clj": "clojure", ".cljs": "clojure", ".cljc": "clojure", ".edn": "clojure",
    ".elm": "elm", ".jl": "julia", ".r": "r",
    ".pl": "perl", ".pm": "perl",
    ".groovy": "groovy", ".gradle": "groovy",
    ".dart": "dart", ".zig": "zig", ".nim": "nim", ".cr": "crystal", ".d": "d",
    ".sol": "solidity", ".mm": "objc", ".m": "matlab",
    ".tcl": "tcl", ".lisp": "commonlisp", ".scm": "scheme", ".rkt": "racket",
    ".gleam": "gleam", ".odin": "odin",
    ".glsl": "glsl", ".vert": "glsl", ".frag": "glsl", ".hlsl": "hlsl", ".wgsl": "wgsl",
}

# Exact filenames -> language id (no/odd extension)
LANG_BY_NAME: dict[str, str] = {
    "Dockerfile": "dockerfile", "dockerfile": "dockerfile",
    "docker-compose.yml": "yaml", "docker-compose.yaml": "yaml",
    "Makefile": "makefile", "makefile": "makefile", "GNUmakefile": "makefile",
    "Jenkinsfile": "groovy", "Vagrantfile": "ruby", "Gemfile": "ruby", "Rakefile": "ruby",
    ".gitignore": "plaintext", ".dockerignore": "plaintext",
    "requirements.txt": "plaintext", "go.mod": "go", "go.sum": "plaintext",
}

CODE_LANGS = {
    "python", "javascript", "typescript", "go", "rust", "ruby", "php", "java", "kotlin",
    "swift", "scala", "c", "cpp", "csharp", "lua", "vue", "svelte",
    # extended coverage
    "vhdl", "verilog", "cobol", "fortran", "ada", "pascal", "haskell", "ocaml", "elixir",
    "erlang", "clojure", "elm", "julia", "r", "perl", "groovy", "dart", "zig", "nim",
    "crystal", "d", "solidity", "objc", "matlab", "tcl", "commonlisp", "scheme", "racket",
    "gleam", "odin", "glsl", "hlsl", "wgsl",
}
CONFIG_LANGS = {"json", "yaml", "toml", "ini", "env", "xml"}
DOC_LANGS = {"markdown", "restructuredtext", "plaintext"}
INFRA_LANGS = {"dockerfile", "terraform", "hcl", "kubernetes"}
SCRIPT_LANGS = {"shell", "powershell", "makefile", "groovy"}
DATA_LANGS = {"csv", "sql"}
MARKUP_LANGS = {"html", "css", "graphql", "protobuf"}


def categorize(language: str, rel_path: str) -> str:
    name = rel_path.replace("\\", "/").lower()
    if "/.github/workflows/" in name or name.startswith(".github/workflows/"):
        return "infra"
    if language in CODE_LANGS:
        return "code"
    if language in INFRA_LANGS:
        return "infra"
    if language in SCRIPT_LANGS:
        return "script"
    if language in DOC_LANGS:
        return "docs"
    if language in DATA_LANGS:
        return "data"
    if language in MARKUP_LANGS:
        return "markup"
    if language in CONFIG_LANGS:
        return "config"
    return "config"


def detect_language(path: Path) -> str:
    if path.name in LANG_BY_NAME:
        return LANG_BY_NAME[path.name]
    return LANG_BY_EXT.get(path.suffix.lower(), "")


@dataclass
class ScannedFile:
    path: str          # relative, forward-slash
    language: str
    category: str
    sizeLines: int


@dataclass
class ScanResult:
    root: Path
    files: list[ScannedFile] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    name: str = "project"
    filtered: int = 0


def _count_lines(path: Path) -> int:
    try:
        with path.open("rb") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


# (framework name, marker substrings in dependency manifests)
_FRAMEWORK_MARKERS: list[tuple[str, tuple[str, ...]]] = [
    ("Django", ("django",)), ("Flask", ("flask",)), ("FastAPI", ("fastapi",)),
    ("React", ("react",)), ("Next.js", ("next",)), ("Vue", ("vue",)),
    ("Express", ("express",)), ("Spring", ("spring-boot", "springframework")),
    ("Rails", ("rails",)), ("Gin", ("gin-gonic",)),
    ("Kubernetes", ("apiversion:",)), ("Terraform", ("terraform",)),
]


def _detect_frameworks(root: Path) -> list[str]:
    blobs: list[str] = []
    for manifest in ("package.json", "pyproject.toml", "requirements.txt", "go.mod", "pom.xml", "Gemfile"):
        p = root / manifest
        if p.is_file():
            blobs.append(p.read_text(encoding="utf-8", errors="ignore").lower())
    text = "\n".join(blobs)
    found = []
    for name, markers in _FRAMEWORK_MARKERS:
        if any(m in text for m in markers):
            found.append(name)
    return found


def scan(root: str | Path, max_file_lines: int = 50_000) -> ScanResult:
    root = Path(root).resolve()
    matcher = build_matcher(root)
    result = ScanResult(root=root, name=root.name)
    langs: set[str] = set()

    for dirpath, dirnames, filenames in _walk(root, matcher):
        for fn in filenames:
            abs_path = Path(dirpath) / fn
            rel = abs_path.relative_to(root).as_posix()
            if matcher.is_ignored(rel):
                result.filtered += 1
                continue
            language = detect_language(abs_path)
            if not language:
                result.filtered += 1
                continue
            lines = _count_lines(abs_path)
            if lines > max_file_lines:
                result.filtered += 1
                continue
            category = categorize(language, rel)
            result.files.append(ScannedFile(rel, language, category, lines))
            if language in CODE_LANGS:
                langs.add(language)

    result.languages = sorted(langs)
    result.frameworks = _detect_frameworks(root)
    result.files.sort(key=lambda f: f.path)
    return result


def _walk(root: Path, matcher):
    import os

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored directories in place so os.walk doesn't descend into them.
        dirnames[:] = [d for d in dirnames if not matcher.is_ignored_dir(d)]
        yield dirpath, dirnames, filenames
