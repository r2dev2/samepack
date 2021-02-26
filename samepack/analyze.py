from typing import Set, NamedTuple
from pathlib import Path


__QUOTES = {'"', "'", "`"}


class Module(NamedTuple):
    file_path: Path
    structures: Set[str]


    def embed(self) -> str:
        return self.__get_structure_declaration()

    def __get_structure_declaration(self) -> str:
        return "var " + " = ".join(self.structures) + " = "


def get_dependencies(target: Path, visited=None, deps=None):
    visited = set() if visited is None else visited
    deps = dict() if deps is None else deps

    if target in visited:
        return []
    dependencies = []
    stack = []
    is_importing = 0 # 0 is not yet, 1 is on from, 2 is on target
    import_material = []
    import_target = []
    with open(target, 'r') as fin:
        for line in map(str.strip, fin):
            for token in filter(bool, line.split(' ')):
                if token == "import" and not stack:
                    is_importing = 1
                elif token == "from" and not stack:
                    is_importing = 2
                    import_target = []
                elif is_importing == 0:
                    for c in token:
                        if c in __QUOTES:
                            if stack and c == stack[-1]:
                                stack.pop()
                            else:
                                stack.append(c)
                elif is_importing == 1:
                    import_material.append(token)
                elif is_importing == 2:
                    for c in token + ' ':
                        if stack or not import_target:
                            import_target.append(c)
                            if c in __QUOTES:
                                if stack and c == stack[-1]:
                                    stack.pop()
                                else:
                                    stack.append(c)
                        elif is_importing == 2:
                            t = ''.join(import_target)[1:-1]
                            if t[:1] == ".":
                                t = target.parent / t
                            t = Path(t).resolve()
                            deps[t] = deps.get(t, Module(t, set()))
                            deps[t].structures.add(
                                ''.join(import_material)
                            )
                            dependencies.append(t)
                            import_material = []
                            import_target = []
                            is_importing = []
                            is_importing = 0

    visited.add(target)
    for path in dependencies:
        get_dependencies(path, visited, deps)

    return deps
