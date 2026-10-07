#!/usr/bin/env python3
"""scan_project.py - read a code project and write project.json (facts only, no guessing).

Usage:
    python3 scan_project.py <project_folder> [-o <output_folder>]

Scans Python, JavaScript and TypeScript files. Uses only the standard library.
Default output folder: <project_folder>/.project-visualizer
"""
import argparse
import ast
import json
import os
import posixpath
import re
import sys
from pathlib import Path

IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__", "dist", "build",
    ".next", ".idea", ".vscode", "target", ".cache", "site-packages", ".pytest_cache",
    ".mypy_cache", "coverage", ".ipynb_checkpoints", ".project-visualizer", ".turbo",
}
EXT_LANG = {
    ".py": "python", ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript",
}
ENTRY_NAMES = {
    "main.py", "app.py", "server.py", "run.py", "manage.py", "cli.py", "__main__.py",
    "index.js", "index.ts", "index.jsx", "index.tsx", "server.js", "app.js", "main.js",
    "main.ts", "main.jsx", "main.tsx",
}
NODE_BUILTINS = {
    "fs", "path", "os", "http", "https", "url", "crypto", "util", "stream", "events",
    "child_process", "zlib", "assert", "buffer", "net", "readline", "process",
}
STDLIB = set(getattr(sys, "stdlib_module_names", ()))
HTTP_METHODS = {"get", "post", "put", "delete", "patch", "route", "websocket"}
JS_EXTS = ["", ".js", ".jsx", ".ts", ".tsx", ".mjs",
           "/index.js", "/index.jsx", "/index.ts", "/index.tsx"]
MAX_BYTES = 800_000

RE_FROM = re.compile(r"""(?:import|export)\s[^'";]*?\sfrom\s*['"]([^'"]+)['"]""")
RE_BARE = re.compile(r"""(?:import\s*|require\(\s*|import\(\s*)['"]([^'"]+)['"]""")
RE_JS_ROUTE = re.compile(
    r"""\b(?:app|router|server|api)\.(get|post|put|delete|patch|use)\(\s*['"`]([^'"`]+)['"`]""")
RE_JS_FUNC = re.compile(
    r"""function\s+(\w+)|(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>""")
RE_JS_CLASS = re.compile(r"\bclass\s+(\w+)")
RE_JS_ENV = re.compile(r"process\.env\.(\w+)|import\.meta\.env\.(\w+)")
RE_PY_ENV = re.compile(
    r"""os\.(?:getenv|environ\.get)\(\s*['"](\w+)['"]|os\.environ\[\s*['"](\w+)['"]""")
RE_HTTP_JS = re.compile(r"""\b(?:fetch|axios\.(?:get|post|put|delete|patch))\(\s*[`'"]([^`'"]+)""")
RE_HTTP_PY = re.compile(
    r"""\b(?:requests|httpx|client|session)\.(?:get|post|put|delete|patch)\(\s*f?['"]([^'"]+)""")
RE_MAIN_GUARD = re.compile(r"""if\s+__name__\s*==\s*['"]__main__['"]""")


def analyze_python(text):
    r = {"imports": [], "functions": [], "classes": [], "routes": [], "doc": ""}
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError) as e:
        r["parse_error"] = str(e)[:120]
        return r
    doc = ast.get_docstring(tree) or ""
    r["doc"] = doc.strip().split("\n")[0][:200]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            r["imports"] += [(0, a.name, []) for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            r["imports"].append((node.level, node.module or "", [a.name for a in node.names]))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in node.decorator_list:
                if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                        and d.func.attr in HTTP_METHODS and d.args
                        and isinstance(d.args[0], ast.Constant)
                        and isinstance(d.args[0].value, str)):
                    r["routes"].append({"method": d.func.attr.upper(),
                                        "path": d.args[0].value, "handler": node.name})
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            r["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            r["classes"].append(node.name)
    return r


def analyze_js(text):
    imports = RE_FROM.findall(text) + RE_BARE.findall(text)
    funcs = []
    for a, b in RE_JS_FUNC.findall(text):
        name = a or b
        if name and name not in funcs:
            funcs.append(name)
    routes = [{"method": m.upper(), "path": p, "handler": ""}
              for m, p in RE_JS_ROUTE.findall(text)]
    doc = ""
    first = text.lstrip().split("\n", 1)[0].strip()
    if first.startswith("//"):
        doc = first.lstrip("/ ").strip()[:200]
    return {"imports": imports, "functions": funcs, "classes": RE_JS_CLASS.findall(text),
            "routes": routes, "doc": doc}


def build_py_map(paths):
    """dotted module name -> set of files (also registers shorter suffixes)."""
    m = {}
    for p in paths:
        if not p.endswith(".py"):
            continue
        parts = p[:-3].split("/")
        if parts[-1] == "__init__":
            parts = parts[:-1]
        for i in range(len(parts)):
            m.setdefault(".".join(parts[i:]), set()).add(p)
    return m


def resolve_py(path, level, module, names, m):
    if level:
        pkg = path.split("/")[:-1]
        if level - 1 > len(pkg):
            return []
        pkg = pkg[: len(pkg) - (level - 1)]
        full = ".".join(pkg + ([module] if module else []))
    else:
        full = module
    name_hits, full_hits = [], []
    for n in names:
        hit = m.get(f"{full}.{n}" if full else n)
        if hit and len(hit) == 1:
            name_hits.append(next(iter(hit)))
    hit = m.get(full) if full else None
    if hit and len(hit) == 1:
        full_hits.append(next(iter(hit)))
    return [t for t in (name_hits or full_hits) if t != path]


def try_js(base, known):
    stripped = re.sub(r"\.(m?jsx?)$", "", base)
    for b in (base, stripped):
        for e in JS_EXTS:
            if b + e in known:
                return b + e
    return None


def resolve_js(path, spec, known):
    if spec.startswith("."):
        return try_js(posixpath.normpath(posixpath.join(posixpath.dirname(path), spec)), known)
    if spec.startswith(("@/", "~/")):
        rest = spec[2:]
        return try_js("src/" + rest, known) or try_js(rest, known)
    return None


def js_package(spec):
    if spec.startswith((".", "@/", "~/", "node:", "http:", "https:")):
        return None
    parts = spec.split("/")
    name = "/".join(parts[:2]) if spec.startswith("@") else parts[0]
    return None if name in NODE_BUILTINS else name


def scan(root: Path):
    texts, skipped, other = {}, [], 0
    declared = {"python": [], "node": []}
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(d for d in dns if d not in IGNORE_DIRS and not d.endswith(".egg-info"))
        for fn in sorted(fns):
            p = Path(dp) / fn
            rel = p.relative_to(root).as_posix()
            try:
                if fn == "package.json":
                    pj = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
                    for k in ("dependencies", "devDependencies"):
                        declared["node"] += [d for d in pj.get(k, {}) if d not in declared["node"]]
                elif fn.startswith("requirements") and fn.endswith(".txt"):
                    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                        line = line.strip()
                        if line and not line.startswith(("#", "-")):
                            name = re.split(r"[<>=!~\[;\s]", line)[0]
                            if name and name not in declared["python"]:
                                declared["python"].append(name)
            except (OSError, ValueError):
                pass
            if p.suffix.lower() not in EXT_LANG:
                other += 1
                continue
            try:
                if p.stat().st_size > MAX_BYTES:
                    skipped.append(rel)
                    continue
                texts[rel] = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                skipped.append(rel)

    known = set(texts)
    py_map = build_py_map(known)
    local_tops = {k.split(".")[0] for k in py_map}
    edges, ext_users, files = set(), {}, []

    for rel in sorted(texts):
        text = texts[rel]
        lang = EXT_LANG[Path(rel).suffix.lower()]
        if lang == "python":
            a = analyze_python(text)
            env = {x for t in RE_PY_ENV.findall(text) for x in t if x}
            http = RE_HTTP_PY.findall(text)
            for level, module, names in a["imports"]:
                targets = resolve_py(rel, level, module, names, py_map)
                edges.update((rel, t) for t in targets)
                if not targets and level == 0 and module:
                    top = module.split(".")[0]
                    if top not in STDLIB and top not in local_tops:
                        ext_users.setdefault(top, set()).add(rel)
        else:
            a = analyze_js(text)
            env = {x for t in RE_JS_ENV.findall(text) for x in t if x}
            http = RE_HTTP_JS.findall(text)
            for spec in a["imports"]:
                t = resolve_js(rel, spec, known)
                if t and t != rel:
                    edges.add((rel, t))
                elif not t:
                    pkg = js_package(spec)
                    if pkg:
                        ext_users.setdefault(pkg, set()).add(rel)
        rec = {
            "path": rel, "language": lang, "lines": text.count("\n") + 1,
            "group": rel.split("/")[0] if "/" in rel else "(root)",
            "doc": a["doc"], "functions": a["functions"][:40], "classes": a["classes"][:40],
            "routes": a["routes"][:40], "env_vars": sorted(env),
            "http_calls": sorted(set(http))[:20],
        }
        if "parse_error" in a:
            rec["parse_error"] = a["parse_error"]
        reasons = []
        if Path(rel).name in ENTRY_NAMES:
            reasons.append("common entry file name")
        if lang == "python" and RE_MAIN_GUARD.search(text):
            reasons.append("has a __main__ block")
        if rec["routes"]:
            reasons.append("defines API routes")
        rec["entry_reasons"] = reasons
        files.append(rec)

    return {
        "root": root.name,
        "stats": {"code_files": len(files), "connections": len(edges),
                  "other_files_ignored": other, "skipped_too_big": skipped},
        "files": files,
        "edges": [{"from": a, "to": b} for a, b in sorted(edges)],
        "external": [{"name": k, "used_by": sorted(v)} for k, v in sorted(ext_users.items())],
        "declared_dependencies": declared,
        "entry_points": [f["path"] for f in files if f["entry_reasons"]],
    }


def main():
    ap = argparse.ArgumentParser(description="Scan a project and write project.json")
    ap.add_argument("project", help="project folder")
    ap.add_argument("-o", "--out", help="output folder (default: <project>/.project-visualizer)")
    args = ap.parse_args()
    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"ERROR: {root} is not a folder")
    out = Path(args.out).expanduser().resolve() if args.out else root / ".project-visualizer"
    out.mkdir(parents=True, exist_ok=True)
    data = scan(root)
    (out / "project.json").write_text(json.dumps(data, indent=2, ensure_ascii=False),
                                      encoding="utf-8")
    s = data["stats"]
    print(f"Scanned {s['code_files']} code files, {s['connections']} connections.")
    print(f"Entry points: {', '.join(data['entry_points']) or 'none found'}")
    print(f"Wrote {out / 'project.json'}")
    if s["code_files"] == 0:
        print("WARNING: no Python/JavaScript/TypeScript files found.")


if __name__ == "__main__":
    main()
