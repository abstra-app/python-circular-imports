from pathlib import Path
from typing import Set, List
import ast
from typing import Optional


def path2module(path: Path) -> str:
    if path.suffix == ".py":
        path = path.with_suffix("")
    if path.name == "__init__":
        path = path.parent
    return str(path).replace("/", ".").replace("\\", ".")


def module2path(module: str, package: bool) -> Path:
    path_list = module.split(".")

    is_first_trailing_dot = True
    for index, path in enumerate(path_list):
        if path.__len__() == 0:
            if is_first_trailing_dot:
                path_list[index] = "."
                is_first_trailing_dot = False
            else:
                path_list[index] = ".."
        else:
            break

    if package:
        path_list.append("__init__.py")
    else:
        path_list[-1] += ".py"
    return Path(*path_list)


def iter_modules(module: str):
    module_blocks = module.split(".")

    yield module
    for i in range(1, len(module_blocks)):
        yield ".".join(module_blocks[:-i])


class DependencyFinder(ast.NodeVisitor):
    deps: Set[Path]
    typechecking_imported_name: Optional[str]
    typing_imported_name: Optional[str]
    in_type_checking_block: bool
    code_path: Path
    base_path: Path
    excluded_patterns: List[str]

    def __init__(self, base_path: Path, excluded_patterns: List[str], code_path: Path):
        self.code_path = code_path
        self.typechecking_imported_name = None
        self.typing_imported_name = None
        self.in_type_checking_block = False
        self.deps = set()
        self.base_path = base_path
        self.excluded_patterns = excluded_patterns

    def visit_Import(self, node: ast.Import):
        if self.in_type_checking_block:
            return
        for alias in node.names:
            if any(e in alias.name for e in self.excluded_patterns):
                continue
            module = alias.name

            for module in iter_modules(module):
                module_path = self.base_path / module2path(module, False)
                if module_path.exists() and not any(
                    e in module_path.name for e in self.excluded_patterns
                ):
                    self.deps.add(module_path.relative_to(self.base_path))

                module_path = self.base_path / module2path(module, True)
                if module_path.exists() and not any(
                    e in module_path.name for e in self.excluded_patterns
                ):
                    self.deps.add(module_path.relative_to(self.base_path))

        if node.names == ["typing"]:
            for alias in node.names:
                if alias.name == "TYPE_CHECKING":
                    self.typechecking_imported_name = alias.asname or alias.name
                elif alias.name == "typing":
                    self.typing_imported_name = alias.asname or alias.name

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if self.in_type_checking_block:
            return
        if node.module is None or any(e in node.module for e in self.excluded_patterns):
            return
        module = node.module

        if node.level == 0:
            search_path = self.base_path
        else:
            search_path = self.code_path.parent
            for _ in range(node.level - 1):
                search_path = search_path.parent

        for module in iter_modules(module):
            module_path = search_path / module2path(module, True)
            if module_path.exists() and not any(
                e in module_path.name for e in self.excluded_patterns
            ):
                self.deps.add(module_path.relative_to(self.base_path))

            module_path = search_path / module2path(module, False)
            if module_path.exists() and not any(
                e in module_path.name for e in self.excluded_patterns
            ):
                self.deps.add(module_path.relative_to(self.base_path))

        if node.module == "typing":
            for alias in node.names:
                if alias.name == "TYPE_CHECKING":
                    self.typechecking_imported_name = alias.asname or alias.name
                elif alias.name == "typing":
                    self.typing_imported_name = alias.asname or alias.name

    def visit_If(self, node: ast.If):
        # if TYPE_CHECKING:
        if (
            self.typechecking_imported_name is not None
            and isinstance(node.test, ast.Name)
            and node.test.id == self.typechecking_imported_name
        ):
            self.in_type_checking_block = True
            self.generic_visit(node)
            self.in_type_checking_block = False

        # if typing.TYPE_CHECKING:
        elif (
            self.typing_imported_name is not None
            and isinstance(node.test, ast.Attribute)
            and node.test.attr == "TYPE_CHECKING"
            and isinstance(node.test.value, ast.Name)
            and node.test.value.id == self.typing_imported_name
        ):
            self.in_type_checking_block = True
            self.generic_visit(node)
            self.in_type_checking_block = False

        else:
            self.generic_visit(node)


def find_deps(
    base_path: Path, code_path: Path, excluded_patterns: List[str]
) -> Set[Path]:
    code = code_path.read_text("utf-8")
    tree = ast.parse(code)
    visitor = DependencyFinder(base_path, excluded_patterns, code_path)
    visitor.visit(tree)

    return visitor.deps
