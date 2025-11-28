# hook-numpy.core.py
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("numpy.core")

# Excluir módulos problemáticos
excludedimports = ["numpy.core._add_newdocs"]
