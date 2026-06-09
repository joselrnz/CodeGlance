"""Languages handled by the generic node-kind classifier (no per-language tuning).

One entry per language: its tree-sitter grammar name. The shared generic walker
extracts functions / types / variables by matching node-kind suffixes, so these
need no bespoke spec. Terraform/HCL parse with their grammars here but use a
dedicated block extractor downstream.
"""

from ..registry import register_generic

# scan language id -> tree-sitter-language-pack grammar name
GENERIC_GRAMMARS = {
    "vhdl": "vhdl", "cobol": "cobol", "fortran": "fortran", "ada": "ada", "verilog": "verilog",
    "haskell": "haskell", "ocaml": "ocaml", "erlang": "erlang", "elixir": "elixir",
    "julia": "julia", "dart": "dart", "solidity": "solidity", "objc": "objc", "groovy": "groovy",
    "perl": "perl", "pascal": "pascal", "zig": "zig", "nim": "nim", "crystal": "crystal", "d": "d",
    "clojure": "clojure", "elm": "elm", "r": "r", "matlab": "matlab", "powershell": "powershell",
    "tcl": "tcl", "commonlisp": "commonlisp", "scheme": "scheme", "racket": "racket",
    "gleam": "gleam", "odin": "odin", "glsl": "glsl", "hlsl": "hlsl", "wgsl": "wgsl",
    "shell": "bash", "terraform": "terraform", "hcl": "hcl",
}

for _lang, _grammar in GENERIC_GRAMMARS.items():
    register_generic(_lang, _grammar)
