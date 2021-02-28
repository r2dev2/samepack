import random
from pathlib import Path
from typing import Dict, List, Optional, Set

from samepack.analyze import Module, get_dependencies


def build(target: Path) -> str:
    index = Module(target, set())
    bundle = []
    deps, tree = get_dependencies(target.resolve())
    for mod_path in __topological_sort(tree, target.resolve()):
        bundle.append(deps[mod_path].embed())
    bundle.append(index.embed_main())
    return "\n\n".join(bundle)


def __topological_sort(
    edges: Dict[Path, Path],
    key: Path,
    path: Optional[List[Path]] = None,
    visited: Optional[Set[Path]] = None,
):
    if path is None:
        path = []
    if visited is None:
        visited = set()

    for k in edges.get(key, []):
        if k not in visited:
            visited.add(k)
            __topological_sort(edges, k, path, visited)
            path.append(k)

    return path
