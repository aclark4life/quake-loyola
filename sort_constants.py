"""
Topological + alphabetical sort for constants.py.

Reads constants.py, preserves the header (imports + legend comment block),
then re-emits all constant assignments and function definitions in dependency
order with alphabetical tie-breaking.

Usage:
    python sort_constants.py        # sorts in-place
    python sort_constants.py --check  # exits 1 if file is not already sorted
"""

import ast
import sys


CONSTANTS_FILE = "constants.py"


def parse_entries(source: str) -> tuple[str, list[dict]]:
    """Return (header, entries).

    header  — everything before the first top-level assignment/def
    entries — list of dicts: { name, code, deps, lineno }
    """
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)

    top_nodes = [
        n
        for n in tree.body
        if isinstance(
            n,
            (
                ast.Assign,
                ast.AugAssign,
                ast.AnnAssign,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    ]

    if not top_nodes:
        return source, []

    header_end = top_nodes[0].lineno - 1  # 0-based
    header = "".join(lines[:header_end])

    entries = []
    for i, node in enumerate(top_nodes):
        start = node.lineno - 1
        end = top_nodes[i + 1].lineno - 1 if i + 1 < len(top_nodes) else len(lines)
        code = "".join(lines[start:end])

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
        elif isinstance(node, ast.Assign):
            # Handle tuple unpacking: a, b = ...
            target = node.targets[0]
            if isinstance(target, ast.Name):
                name = target.id
            elif isinstance(target, ast.Tuple):
                # Use the first element as the canonical name; track all
                names = [e.id for e in target.elts if isinstance(e, ast.Name)]
                name = names[0] if names else f"_tuple_{i}"
            else:
                name = f"_anon_{i}"
        elif isinstance(node, ast.AnnAssign):
            name = node.target.id if isinstance(node.target, ast.Name) else f"_anon_{i}"
        else:
            name = f"_anon_{i}"

        entries.append({"name": name, "code": code, "deps": set()})

    # Collect ALL names introduced by each entry (handles tuple unpacking like A, B = ...)
    entry_names: list[set[str]] = []
    for node in top_nodes:
        names: set[str] = set()
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
                elif isinstance(target, ast.Tuple):
                    names.update(e.id for e in target.elts if isinstance(e, ast.Name))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                names.add(node.target.id)
        entry_names.append(names)

    # Build the full set of defined names — register ALL names from each entry
    all_defined: dict[str, int] = {}
    for i, self_names_set in enumerate(entry_names):
        for n in self_names_set:
            all_defined[n] = i

    # Map every defined name → the canonical entry name that defines it
    # Needed for tuple unpacking: `PB_DZ1, PB_DZ2 = ...` has canonical name PB_DZ1
    # but PB_DZ2 must also be tracked as a dep trigger.
    name_to_canonical = {n: entries[idx]["name"] for n, idx in all_defined.items()}

    # Compute deps as canonical entry names that must precede this entry
    for entry, node, self_names in zip(entries, top_nodes, entry_names):
        used = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
        used -= self_names  # remove names this entry itself defines
        deps: set[str] = set()
        for name in used:
            canonical = name_to_canonical.get(name)
            if canonical and canonical != entry["name"]:
                deps.add(canonical)
        entry["deps"] = deps

    return header, entries


def topo_alpha_sort(entries: list[dict]) -> list[dict]:
    """Kahn's algorithm with alphabetical tie-breaking."""
    name_to_entry = {e["name"]: e for e in entries}

    dependents: dict[str, set[str]] = {e["name"]: set() for e in entries}
    in_degree: dict[str, int] = {e["name"]: 0 for e in entries}

    for entry in entries:
        for dep in entry["deps"]:
            if dep in dependents:
                dependents[dep].add(entry["name"])
                in_degree[entry["name"]] += 1

    ready = sorted(n for n, deg in in_degree.items() if deg == 0)

    result = []
    while ready:
        name = ready.pop(0)
        result.append(name_to_entry[name])
        newly_ready = []
        for dependent in dependents[name]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                newly_ready.append(dependent)
        ready = sorted(ready + newly_ready)

    if len(result) != len(entries):
        # Cycle fallback — append remaining in original order
        emitted = {e["name"] for e in result}
        result.extend(e for e in entries if e["name"] not in emitted)

    return result


def sorted_source(header: str, entries: list[dict]) -> str:
    sorted_entries = topo_alpha_sort(entries)
    body = "\n".join(e["code"].rstrip("\n") for e in sorted_entries)
    return header + body + "\n"


def main():
    check_mode = "--check" in sys.argv

    with open(CONSTANTS_FILE) as f:
        original = f.read()

    header, entries = parse_entries(original)
    result = sorted_source(header, entries)

    # Validate: ensure the result actually imports cleanly
    try:
        compile(result, CONSTANTS_FILE, "exec")
    except SyntaxError as e:
        print(f"ERROR: sorted result has syntax error: {e}")
        sys.exit(2)

    if check_mode:
        if result != original:
            print("constants.py is not sorted — run: python sort_constants.py")
            sys.exit(1)
        else:
            print("constants.py is already sorted.")
    else:
        if result != original:
            with open(CONSTANTS_FILE, "w") as f:
                f.write(result)
            print("constants.py sorted.")
        else:
            print("constants.py already sorted, nothing to do.")


if __name__ == "__main__":
    main()
