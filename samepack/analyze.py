import re
from pathlib import Path
from typing import Dict, NamedTuple, Optional, Set

QUOTES = {'"', "'", "`"}
EXPORTABLES = {"let", "const", "function", "class", "var"}


class Module(NamedTuple):
    file_path: Path
    structures: Set[str]

    def embed(self) -> str:
        if self.file_path.is_dir():
            return ""
        contents = self.__get_module_contents()
        exports = self.__to_return(self.__get_exports(contents))
        module_contents = self.__remove_exports(contents)
        struct_decl = self.__get_structure_declaration()
        return self.__combine_module_pieces(struct_decl, exports, module_contents)

    def embed_main(self) -> str:
        return self.__remove_exports(self.__get_module_contents())

    def __get_module_contents(self) -> str:
        with open(self.file_path, "r") as fin:
            return re.sub(
                r"import \w+ from",
                "//",
                re.sub(r"import {[^}]*} from", "//", fin.read()),
            )

    @staticmethod
    def __combine_module_pieces(
        struct_decl: str, exports: str, module_contents: str
    ) -> str:
        return "\n".join(
            [
                f"{struct_decl} (() => " "{",
                module_contents,
                exports,
                "})();",
            ]
        )

    @staticmethod
    def __remove_exports(contents: str) -> str:
        buff = []
        for line in contents.split("\n"):
            if line[:7] == "export ":
                buff.append(line[7:])
            else:
                buff.append(line)
        return "\n".join(buff)

    @staticmethod
    def __to_return(exports: Set[str]) -> str:
        return "return {" f"{', '.join(exports)}" "};"

    @staticmethod
    def __get_exports(module: str) -> Set[str]:
        wout_quotes = Module.__remove_quoted(module)
        words = []
        exports = set()
        for word in filter(bool, re.split(r"\W+", wout_quotes)):
            if Module.__endswith_general_export(words) or Module.__endswith_async_export(words):
                exports.add(word)
            words.append(word)
        return exports

    @staticmethod
    def __endswith_async_export(words: str) -> bool:
        return len(words) >= 3 and words[-3:] == ["export", "async", "function"]

    @staticmethod
    def __endswith_general_export(words: str) -> bool:
        return len(words) >= 2 and words[-2] == "export" and words[-1] in EXPORTABLES

    @staticmethod
    def __remove_quoted(module: str) -> str:
        s = module
        for q in QUOTES:
            s = re.sub(f"{q}[^{q}]*{q}", "", s)
        return s

    def __get_structure_declaration(self) -> str:
        return "var " + " = ".join(self.structures) + " = "


def get_dependencies(
    target: Path,
    visited: Optional[Set[Path]] = None,
    deps: Optional[Dict[Path, Module]] = None,
    tree: Optional[Dict[Path, Set[Path]]] = None,
) -> Dict[Path, Module]:
    visited = set() if visited is None else visited
    deps = dict() if deps is None else deps
    tree = dict() if tree is None else tree

    if target in visited or target.is_dir():
        return []
    dependencies = []
    stack = []
    is_importing = 0  # 0 is not yet, 1 is on from, 2 is on target
    import_material = []
    import_target = []
    with open(target, "r") as fin:
        for line in map(str.strip, fin):
            for token in filter(bool, line.split(" ")):
                if token == "import" and not stack:
                    is_importing = 1
                elif token == "from" and not stack:
                    is_importing = 2
                    import_target = []
                elif is_importing == 0:
                    for c in token:
                        if c in QUOTES:
                            if stack and c == stack[-1]:
                                stack.pop()
                            else:
                                stack.append(c)
                elif is_importing == 1:
                    import_material.append(token)
                elif is_importing == 2:
                    for c in token + " ":
                        if stack or not import_target:
                            import_target.append(c)
                            if c in QUOTES:
                                if stack and c == stack[-1]:
                                    stack.pop()
                                else:
                                    stack.append(c)
                        elif is_importing == 2:
                            t = "".join(import_target)[1:-1]
                            if t[:1] == ".":
                                t = target.parent / t
                            t = Path(t).resolve()
                            deps[t] = deps.get(t, Module(t, set()))
                            deps[t].structures.add("".join(import_material))
                            dependencies.append(t)
                            tree[target] = tree.get(target, set())
                            tree[target].add(t)
                            import_material = []
                            import_target = []
                            is_importing = []
                            is_importing = 0

    visited.add(target)
    for path in dependencies:
        get_dependencies(path, visited, deps, tree)

    return deps, tree
