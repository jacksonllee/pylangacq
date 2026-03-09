# PyLangAcq documentation build configuration file, created by
# sphinx-quickstart on Mon Dec 28 22:50:02 2015.

import ast
import os
from datetime import date
from pathlib import Path

import pylangacq
import rustling

# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    "sphinx.ext.napoleon",
    'sphinx.ext.intersphinx',
    "sphinx_copybutton",
]


# ---------------------------------------------------------------------------
# Parse .pyi stubs from rustling so autodoc can use them for re-exported classes.
# autodoc introspects runtime (PyO3) objects, which only carry the Rust /// doc
# comment.  The .pyi stubs have richer per-attribute docstrings that we inject
# via the autodoc-process-docstring event.
# ---------------------------------------------------------------------------

def _unparse_annotation(node):
    """Convert an AST annotation node to a string."""
    return ast.unparse(node) if node else ""


def _build_signature(func_node):
    """Build a signature string from an AST FunctionDef node.

    Skips ``self`` and ``cls`` parameters. Returns e.g.
    ``"(path: str | os.PathLike[str], *, match: str | None = None) -> CHAT"``.
    """
    args = func_node.args
    parts = []

    # Positional args (skip self/cls)
    positional = args.args
    defaults = args.defaults
    # defaults align to the end of positional args
    n_no_default = len(positional) - len(defaults)
    for i, arg in enumerate(positional):
        if arg.arg in ("self", "cls"):
            continue
        s = arg.arg
        if arg.annotation:
            s += f": {ast.unparse(arg.annotation)}"
        di = i - n_no_default
        if di >= 0:
            s += f" = {ast.unparse(defaults[di])}"
        parts.append(s)

    # *args or bare *
    if args.vararg:
        va = f"*{args.vararg.arg}"
        if args.vararg.annotation:
            va += f": {ast.unparse(args.vararg.annotation)}"
        parts.append(va)
    elif args.kwonlyargs:
        parts.append("*")

    # Keyword-only args
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        s = arg.arg
        if arg.annotation:
            s += f": {ast.unparse(arg.annotation)}"
        if default is not None:
            s += f" = {ast.unparse(default)}"
        parts.append(s)

    sig = f"({', '.join(parts)})"
    if func_node.returns:
        sig += f" -> {ast.unparse(func_node.returns)}"
    return sig


def _parse_pyi_classes():
    """Walk rustling's .pyi stubs and collect class info.

    Returns a dict mapping fully qualified class name to a dict with:
        - "docstring": the class docstring
        - "attributes": list of (name, type_str, docstring) tuples
        - "methods": list of (name, signature, docstring) tuples
    """
    result = {}
    rustling_dir = Path(os.path.dirname(rustling.__file__))
    for pyi_path in rustling_dir.rglob("*.pyi"):
        rel = pyi_path.relative_to(rustling_dir.parent)
        parts = list(rel.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        mod_name = ".".join(parts)

        tree = ast.parse(pyi_path.read_text())
        for node in ast.iter_child_nodes(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            cls_fqn = f"{mod_name}.{node.name}"
            cls_info = {
                "docstring": ast.get_docstring(node) or "",
                "attributes": [],
                "methods": [],
            }
            body = node.body
            for i, stmt in enumerate(body):
                # Attributes: AnnAssign possibly followed by docstring
                if isinstance(stmt, ast.AnnAssign) and isinstance(
                    stmt.target, ast.Name
                ):
                    attr_name = stmt.target.id
                    type_str = _unparse_annotation(stmt.annotation)
                    doc = ""
                    if i + 1 < len(body):
                        nxt = body[i + 1]
                        if (
                            isinstance(nxt, ast.Expr)
                            and isinstance(nxt.value, ast.Constant)
                            and isinstance(nxt.value.value, str)
                        ):
                            doc = nxt.value.value
                    cls_info["attributes"].append((attr_name, type_str, doc))
                # Methods
                elif isinstance(stmt, ast.FunctionDef):
                    mds = ast.get_docstring(stmt)
                    if mds:
                        sig = _build_signature(stmt)
                        cls_info["methods"].append((stmt.name, sig, mds))
            result[cls_fqn] = cls_info
    return result


_PYI_CLASSES = _parse_pyi_classes()

# Map pylangacq names to their rustling origins.
# PyO3 classes report __module__ as "builtins", so we build the mapping
# by matching class names against pylangacq.__all__.
_PYLANGACQ_TO_RUSTLING = {}
for _pyi_fqn in _PYI_CLASSES:
    _cls_name = _pyi_fqn.rsplit(".", 1)[-1]
    if _cls_name in pylangacq.__all__:
        _PYLANGACQ_TO_RUSTLING[f"pylangacq.{_cls_name}"] = _pyi_fqn


def _autodoc_process_docstring(app, what, name, obj, options, lines):
    """Replace runtime docstrings with .pyi content for rustling classes."""
    rustling_fqn = _PYLANGACQ_TO_RUSTLING.get(name)
    if not rustling_fqn or rustling_fqn not in _PYI_CLASSES:
        # For attributes/methods: try parent class mapping
        parts = name.rsplit(".", 1)
        if len(parts) == 2:
            parent, member = parts
            rustling_parent = _PYLANGACQ_TO_RUSTLING.get(parent)
            if rustling_parent:
                info = _PYI_CLASSES.get(rustling_parent)
                if info:
                    for mname, _msig, mdoc in info["methods"]:
                        if mname == member:
                            lines.clear()
                            lines.extend(mdoc.splitlines())
                            return
        return

    info = _PYI_CLASSES[rustling_fqn]

    lines.clear()
    # Class docstring
    if info["docstring"]:
        lines.extend(info["docstring"].splitlines())

    # Attributes as rst field list
    if info["attributes"]:
        lines.append("")
        for attr_name, type_str, doc in info["attributes"]:
            lines.append(f".. attribute:: {attr_name}")
            lines.append(f"   :type: {type_str}")
            lines.append("")
            if doc:
                lines.append(f"   {doc}")
                lines.append("")


# Collect attribute names per class so we can skip them in autodoc-skip-member.
_RUSTLING_ATTR_NAMES = {}
for _fqn, _info in _PYI_CLASSES.items():
    _cls_name = _fqn.rsplit(".", 1)[-1]
    if f"pylangacq.{_cls_name}" in _PYLANGACQ_TO_RUSTLING:
        _RUSTLING_ATTR_NAMES[_cls_name] = {a[0] for a in _info["attributes"]}


def _autodoc_process_signature(app, what, name, obj, options, signature, return_annotation):
    """Override signatures for rustling methods with .pyi stub signatures."""
    if what == "method":
        parts = name.rsplit(".", 1)
        if len(parts) == 2:
            parent, member = parts
            rustling_parent = _PYLANGACQ_TO_RUSTLING.get(parent)
            if rustling_parent:
                info = _PYI_CLASSES.get(rustling_parent)
                if info:
                    for mname, msig, _mdoc in info["methods"]:
                        if mname == member:
                            return msig, None
    elif what == "class":
        rustling_fqn = _PYLANGACQ_TO_RUSTLING.get(name)
        if rustling_fqn:
            info = _PYI_CLASSES.get(rustling_fqn)
            if info:
                for mname, msig, _mdoc in info["methods"]:
                    if mname == "__init__":
                        return msig, None
    return None


def _autodoc_skip_member(app, what, name, obj, skip, options):
    """Skip attributes already injected via .. attribute:: in the class docstring.

    Only skip attributes (not methods), so :members: still renders methods.
    """
    if what == "class" and not callable(obj):
        # obj is the member (e.g. a getset_descriptor); check if it belongs
        # to a rustling class by looking at the descriptor's __objclass__.
        objclass = getattr(obj, "__objclass__", None)
        if objclass is not None:
            cls_name = objclass.__qualname__
            attr_names = _RUSTLING_ATTR_NAMES.get(cls_name, set())
            if name in attr_names:
                return True  # skip — we already injected it
    return None  # defer to default


def setup(app):
    # Priority 400 so this runs BEFORE Napoleon (priority 500), which then
    # converts the injected Google-style docstrings into proper RST.
    app.connect("autodoc-process-docstring", _autodoc_process_docstring, priority=400)
    app.connect("autodoc-process-signature", _autodoc_process_signature)
    app.connect("autodoc-skip-member", _autodoc_skip_member)


templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'PyLangAcq'
author = 'Jackson L. Lee'
html_author_link = author  # can't use the next line?
# html_author_link = '<a href="https://jacksonllee.com/">{}</a>'.format(author)
today_ = date.today()
copyright = ('2015-{}, {} | '
             'PyLangAcq {} | '
             'Documentation last updated on {}').format(
    today_.strftime('%Y'),
    html_author_link,
    pylangacq.__version__,
    today_.strftime('%B %d, %Y')
)

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
current_version = pylangacq.__version__

# The short X.Y version.
version = current_version
# The full version, including alpha/beta/rc tags.
release = current_version

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

napoleon_google_docstring = True
napoleon_numpy_docstring = False

autodoc_typehints_format = "fully-qualified"

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'furo'

html_static_path = ['_static']
html_show_sourcelink = False


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": ('https://docs.python.org/3/', None),
    "pycantonese": ('https://docs.pycantonese.org/stable/', None),
    "rustling": ('https://rustling.readthedocs.io/stable/', None),
}
