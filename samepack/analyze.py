from typing import NamedTuple
from pathlib import Path

__QUOTES = {'"', "'", "`"}


class Dependency(NamedTuple):
    structure: str
    file_path: Path

def get_dependencies(target: Path, visited=None):
    if visited is None:
        visited = set()
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
                            dependencies.append(Dependency(
                                ''.join(import_material),
                                Path(t).resolve()
                            ))
                            import_material = []
                            import_target = []
                            is_importing = []
                            is_importing = 0

    visited.add(target)
    for _, path in dependencies[:]:
        dependencies.extend(get_dependencies(path, visited))
    return dependencies
