from pathlib import Path
from typing import Set, Tuple
from find_deps import find_deps
from graph import find_cycles
import fire


class CLI:
    def cycles(self, path: str, exclude: str = None):
        excluded_patterns = list(map(str.strip, exclude.split(","))) if exclude else []
        path_ = Path(path)
        assert path_.exists(), f"Path {path_} does not exist"
        assert path_.is_dir(), f"Path {path_} is not a directory"

        all_python_files: Set[Path] = set(path_.glob('**/*.py'))

        graph: Set[Tuple[str, str]] = set()
        for python_file in all_python_files:
            if any(e in str(python_file) for e in excluded_patterns):
                continue
            deps = find_deps(path_, python_file, excluded_patterns)
            for dep in deps:
                graph.add((str(python_file.relative_to(path_)), str(dep)))
        cycles = find_cycles(graph)

        dot_code = "digraph G {\n"
        for cycle in cycles:
            for i in range(len(cycle)):
                dot_code += f'"{cycle[i]}" -> "{cycle[(i + 1) % len(cycle)]}"\n'
        dot_code += "}"

        print(dot_code)
        

if __name__ == '__main__':
    fire.Fire(CLI)
