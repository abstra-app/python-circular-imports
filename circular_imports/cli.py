from pathlib import Path
from typing import Set, Tuple
from .find_deps import find_deps
from .graph import find_cycles
import fire


def cycles_in_path(path: str, exclude: str = None) -> Set[Tuple[str, str]]:
    excluded_patterns = list(map(str.strip, exclude.split(","))) if exclude else []
    path_ = Path(path)
    assert path_.exists(), f"Path {path_} does not exist"
    assert path_.is_dir(), f"Path {path_} is not a directory"

    all_python_files: Set[Path] = set(path_.glob("**/*.py"))

    graph: Set[Tuple[str, str]] = set()
    for python_file in all_python_files:
        if any(e in str(python_file) for e in excluded_patterns):
            continue
        deps = find_deps(path_, python_file, excluded_patterns)
        for dep in deps:
            graph.add((str(python_file.relative_to(path_)), str(dep)))
    return find_cycles(graph)


def run(path: str, exclude: str = None, output: str = None):
    """
    Find circular imports in a Python project.

    Args:
        path (str): Path to the Python project.
        exclude (str, optional): Comma separated list of patterns to exclude. Defaults to None.
        output (str, optional): Output format. Defaults to None.

    Supported output formats:
    - .dot: Graphviz DOT format
    - .mermaid: Mermaid.js format

    Examples:
    $ circular_imports .

    $ circular_imports . --exclude "tests,docs"

    $ circular_imports . --output graph.dot

    $ circular_imports . --output graph.mermaid
    """
    cycles = cycles_in_path(path, exclude)

    if output is None:
        for cycle in cycles:
            print(" -> ".join(cycle))
    elif output.endswith(".dot"):
        dot_code = "digraph G {\n"
        for cycle in cycles:
            for i in range(len(cycle)):
                dot_code += f'"{cycle[i]}" -> "{cycle[(i + 1) % len(cycle)]}"\n'
        dot_code += "}"

        with open(output, "w") as f:
            f.write(dot_code)
    elif output.endswith(".mermaid"):
        mermaid_code = "graph TD;\n"
        for cycle in cycles:
            for i in range(len(cycle)):
                mermaid_code += f"    {cycle[i]} --> {cycle[(i + 1) % len(cycle)]};\n"

        with open(output, "w") as f:
            f.write(mermaid_code)
    else:
        print(f"Unsupported output format {output}")
        exit(1)

    if len(cycles) > 0:
        exit(1)


def main():
    fire.Fire(run)


if __name__ == "__main__":
    main()
