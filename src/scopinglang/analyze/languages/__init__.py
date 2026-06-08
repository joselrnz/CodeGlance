"""Per-language definitions. Importing this package registers every language.

Tuned languages each get a small module declaring their tree-sitter node-kinds;
the ~35 generic (exotic) languages share ``generic.py``. Add a language by
dropping a new ``<id>.py`` here and listing it below.
"""

from . import (  # noqa: F401  (imports trigger self-registration)
    javascript, typescript, go, rust, java, c, cpp, csharp, ruby, php,
    kotlin, swift, scala, lua, generic,
)
