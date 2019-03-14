import os
import importlib
from importlib import util


def load_modules(package):
    pac_path = package.__path__[0]
    mods_names = os.listdir(pac_path)
    modules = list()
    for mod_name in mods_names:
        if mod_name.startswith('_'):
            continue
        mod_name = 'parsers.' + mod_name.replace('.py', '')
        m = importlib.import_module(mod_name, package)
        modules.append(m)
    return modules
