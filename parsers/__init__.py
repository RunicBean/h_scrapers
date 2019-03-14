import core.ref_utils as cru


def select(store, type):
    pr_mod = __import__(__name__)
    d = dir(pr_mod)

    pr_mods = cru.load_modules(pr_mod)
    for m in pr_mods:
        parser = m.Parser()
        x = parser.store
        if parser.store == store and parser.type == type:
            return parser
