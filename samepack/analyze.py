import re
from pathlib import Path
from typing import Dict, Iterable, NamedTuple, Optional, Set

QUOTES = {'"', "'", "`"}
EXPORTABLES = {"let", "const", "function", "class", "var"}
__file_code_cache: Dict[Path, str] = dict()
__file_codes: Dict[str, int] = dict()


class Import(NamedTuple):
    struct: str
    file_path: Path

    def __str__(self) -> str:
        return f"var {self.struct} = {file_code(self.file_path)};"


class Module(NamedTuple):
    file_path: Path

    def embed(self, main=False) -> str:
        if self.file_path.is_dir():
            return ""
        raw = self.__read_file()
        contents = self.__get_module_contents(raw)
        imports = self.__get_imports(raw)
        exports = self.__to_return(self.__get_exports(contents))
        module_contents = self.__remove_exports(contents)
        struct_decl = self.__get_structure_declaration()
        return self.__combine_module_pieces(struct_decl, imports, exports, module_contents, main)

    def embed_main(self) -> str:
        return self.embed(True)

    def __read_file(self) -> str:
        with open(self.file_path, "r") as fin:
            return fin.read()

    @staticmethod
    def __get_module_contents(raw_contents: str) -> str:
        return re.sub(
            r"import \* as \w+ from",
            "//",
            re.sub(r"import {[^}]*} from", "//", raw_contents),
        )

    @staticmethod
    def __combine_module_pieces(
        struct_decl: str, imports: Iterable[str], exports: str, module_contents: str, main: bool
    ) -> str:
        return "\n".join(
            [
                f"{struct_decl} (() => " "{" if not main else "",
                "",
                *imports,
                "",
                module_contents,
                exports if not main else "",
                "})();" if not main else "",
            ]
        )

    def __get_imports(self, raw_contents: str) -> Iterable[str]:
        return map(str, gen_imports(raw_contents, self.file_path))

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
            if Module.__endswith_general_export(
                words
            ) or Module.__endswith_async_export(words):
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
        return f"var {file_code(self.file_path)} = "


def file_code(fp: Path) -> str:
    full_path = fp.resolve()
    try:
        return __file_code_cache[full_path]
    except KeyError:
        stem = full_path.stem.replace("-", "")
        end_no = __file_codes.get(stem, 0)
        file_code = f"SAME${stem}${end_no}"
        __file_codes[stem] = end_no + 1
        __file_code_cache[full_path] = file_code
        return file_code


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
    with open(target, "r") as fin:
        module = fin.read()

    for _, imp_path in gen_imports(module, target):
        deps[imp_path] = Module(imp_path)
        dependencies.append(imp_path)
        tree[target] = tree.get(target, set())
        tree[target].add(imp_path)

    visited.add(target)
    for path in dependencies:
        get_dependencies(path, visited, deps, tree)

    return deps, tree


def __not_yet_importing(token, stack):
    for c in token:
        __stack_process_char(c, stack)


def __stack_process_char(c, stack):
    if c in QUOTES:
        if stack and c == stack[-1]:
            stack.pop()
        else:
            stack.append(c)


def gen_imports(module: str, base: Path) -> Iterable[Import]:
    importing = 0  # 0 is not yet, 1 is on from, 2 is on target
    import_material, import_target, stack = ([] for _ in range(3))
    for token in re.split(r"[ \n]+", module):
        if token == "import" and not stack:
            importing = 1
        elif token == "from" and not stack:
            importing = 2
        elif importing == 0:
            __not_yet_importing(token, stack)
        elif importing == 1:
            import_material.append(replace_special_token(token))
        elif importing == 2:
            for c in token + " ":
                if stack or not import_target:
                    import_target.append(c)
                    __stack_process_char(c, stack)
                elif c in QUOTES:
                    __stack_process_char(c, stack)
                elif importing == 2:
                    t = "".join(import_target)[1:-1]
                    if t[:1] == ".":
                        t = base.parent / t
                    imp_path = Path(t)
                    joined = join_imports(import_material).strip()
                    if joined:
                        yield Import(
                            joined,
                            imp_path,
                        )
                    import_material = []
                    import_target = []
                    importing = 0


def join_imports(imports: Iterable[str]) -> str:
    return "".join(imports).replace("*:", "")


def replace_special_token(token: str):
    if token == "as":
        return ":"
    return token
