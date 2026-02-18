# PyLangAcq documentation build configuration file, created by
# sphinx-quickstart on Mon Dec 28 22:50:02 2015.

from datetime import date

import pylangacq

# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    "sphinx.ext.napoleon",
    'sphinx.ext.intersphinx',
    "sphinx_copybutton",
]

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


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'furo'

html_static_path = ['_static']
html_show_sourcelink = False


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": ('https://docs.python.org/3/', None),
    "pycantonese": ('https://pycantonese.org', None),
    "rustling": ('https://rustling.readthedocs.io/stable/', None),
}
