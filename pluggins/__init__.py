from pathlib import Path
from pkgutil import iter_modules
from importlib import import_module

package_dir = Path(__file__).resolve().parent
for (_, module_name, _) in iter_modules([package_dir]):
    import_module(f"{__name__}.{module_name}")
        
