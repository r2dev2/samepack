from pathlib import Path

from samepack.analyze import Module, get_dependencies


def build(target: Path) -> str:
    index = Module(target, set())
    bundle = []
    deps = get_dependencies(target)
    list(map(bundle.append, map(Module.embed, deps.values())))
    bundle.append(index.embed_main())
    return "\n\n".join(bundle)
