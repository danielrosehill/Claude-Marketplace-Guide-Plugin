#!/usr/bin/env python3
"""Discovery over a Claude Code plugin marketplace, read live at run time.

The plugin list is never hard-coded: it comes from the marketplace's own
marketplace.json. Themed groups (groups.json, next to this plugin) only name plugins.

Manifest source, first that works:
  1. --manifest PATH            explicit file
  2. groups.json "repo" via `gh api`      freshest; needs gh auth (required for private)
  3. --url / groups.json "manifest_url"   raw GitHub, public only; the CDN serves
     `main` up to ~5 min stale after a push (seen 2026-10-21)
  4. ~/.claude/plugins/marketplaces/<marketplace>/  Claude Code's own clone. Last,
     because it only refreshes on `/plugin marketplace update` and can lag (seen
     2026-10-21: 172 plugins locally vs 178 published). Output carries a warning.

Commands (all print JSON):
  groups                 themed groups and manifest categories, with counts
  group <id>             plugins in one themed group or category (id or title)
  list                   every plugin, compact (name, description, category)
  search <terms...>      keyword-ranked matches over name/description/tags/category
  show <plugin>          one plugin's full manifest entry + install line
  new [--limit N]        recent additions, from CHANGELOG.md (else recent commits via gh)
  check                  groups.json vs manifest: unknown names, ungrouped plugins

Exit codes: 0 ok, 2 manifest unreachable, 3 unknown group/plugin, 4 check found problems.
"""
import argparse, json, os, pathlib, re, sys, urllib.request

HERE = pathlib.Path(__file__).resolve().parent.parent
GROUPS_FILE = HERE / "groups.json"


def load_groups():
    return json.loads(GROUPS_FILE.read_text())


def fetch(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return r.read().decode()


def gh_file(repo, path):
    import subprocess
    r = subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}", "-H", "Accept: application/vnd.github.raw"],
                       capture_output=True, text=True, timeout=30)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:200])
    return r.stdout


def load_manifest(args, cfg):
    """Return (manifest, source, changelog_text_or_None, warning_or_None).

    Live sources first: Claude Code's local clone only refreshes on
    `/plugin marketplace update`, so it can silently lag the published manifest.
    """
    name = args.marketplace or cfg["marketplace"]
    own = name == cfg["marketplace"]
    tried = []
    if args.manifest:
        try:
            return json.loads(pathlib.Path(args.manifest).read_text()), args.manifest, None, None
        except Exception as e:
            out({"error": f"cannot read --manifest: {e}"}, 2)
    repo = cfg.get("repo") if own and not args.url else None
    if repo:
        try:
            m = json.loads(gh_file(repo, ".claude-plugin/marketplace.json"))
            try:
                cl = gh_file(repo, "CHANGELOG.md")
            except Exception:
                cl = None
            return m, f"gh api {repo}", cl, None
        except Exception as e:
            tried.append(f"gh api {repo} ({e})")
    url = args.url or (cfg.get("manifest_url") if own else None)
    if url:
        try:
            m = json.loads(fetch(url))
            cl = None
            if own and cfg.get("changelog_url"):
                try:
                    cl = fetch(cfg["changelog_url"])
                except Exception:
                    pass
            return m, url, cl, None
        except Exception as e:
            tried.append(f"{url} ({e})")
    local = pathlib.Path.home() / ".claude/plugins/marketplaces" / name
    lm = local / ".claude-plugin/marketplace.json"
    if lm.exists():
        cl = local / "CHANGELOG.md"
        warn = ("Read Claude Code's local copy because the live manifest was unreachable; it may be "
                "out of date. Run `/plugin marketplace update` to refresh it.")
        return json.loads(lm.read_text()), str(lm), (cl.read_text() if cl.exists() else None), warn
    tried.append(str(lm))
    out({"error": "manifest unreachable", "marketplace": name, "tried": tried,
         "hint": "Add the marketplace in Claude Code (/plugin marketplace add <owner/repo>) or pass --manifest."}, 2)


WARNING = None


def out(obj, code=0):
    if WARNING and isinstance(obj, dict):
        obj = dict(obj, warning=WARNING)
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    sys.exit(code)


def compact(p, mkt):
    return {"name": p["name"], "description": p.get("description", ""),
            "category": p.get("category"), "install": f"/plugin install {p['name']}@{mkt}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marketplace")
    ap.add_argument("--manifest")
    ap.add_argument("--url")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("groups")
    g = sub.add_parser("group"); g.add_argument("id")
    sub.add_parser("list")
    s = sub.add_parser("search"); s.add_argument("terms", nargs="+"); s.add_argument("--limit", type=int, default=15)
    sh = sub.add_parser("show"); sh.add_argument("plugin")
    n = sub.add_parser("new"); n.add_argument("--limit", type=int, default=3, help="dated sections")
    sub.add_parser("check")
    args = ap.parse_args()

    cfg = load_groups()
    global WARNING
    man, source, changelog, WARNING = load_manifest(args, cfg)
    mkt = man.get("name", cfg["marketplace"])
    plugins = {p["name"]: p for p in man["plugins"]}
    themes = cfg["groups"]
    cats = {}
    for p in man["plugins"]:
        cats.setdefault(p.get("category") or "Uncategorised", []).append(p["name"])

    if args.cmd == "groups":
        out({"marketplace": mkt, "source": source, "plugins": len(plugins),
             "themed_groups": [{"id": t["id"], "title": t["title"], "description": t["description"],
                                "count": sum(1 for x in t["plugins"] if x in plugins)} for t in themes],
             "categories": [{"title": k, "count": len(v)} for k, v in sorted(cats.items(), key=lambda kv: -len(kv[1]))]})

    if args.cmd == "group":
        key = args.id.lower()
        for t in themes:
            if key in (t["id"].lower(), t["title"].lower()):
                out({"group": t["title"], "description": t["description"], "kind": "theme",
                     "plugins": [compact(plugins[x], mkt) for x in t["plugins"] if x in plugins],
                     "missing_from_manifest": [x for x in t["plugins"] if x not in plugins]})
        for k, v in cats.items():
            if key == k.lower():
                out({"group": k, "kind": "category", "plugins": [compact(plugins[x], mkt) for x in v]})
        out({"error": f"no group '{args.id}'", "themes": [t["id"] for t in themes], "categories": list(cats)}, 3)

    if args.cmd == "list":
        out({"marketplace": mkt, "source": source, "plugins": [compact(p, mkt) for p in man["plugins"]]})

    if args.cmd == "search":
        terms = [t.lower() for t in args.terms]
        theme_of = {}
        for t in themes:
            for x in t["plugins"]:
                theme_of.setdefault(x, []).append(t["title"])
        scored = []
        for p in man["plugins"]:
            fields = {"name": p["name"] + " " + p.get("displayName", ""), "description": p.get("description", ""),
                      "tags": " ".join(p.get("tags", []) + p.get("keywords", [])),
                      "group": (p.get("category") or "") + " " + " ".join(theme_of.get(p["name"], []))}
            w = {"name": 5, "tags": 3, "group": 2, "description": 1}
            score = sum(w[f] for t in terms for f, v in fields.items() if t in v.lower())
            if score:
                scored.append((score, p))
        scored.sort(key=lambda x: -x[0])
        out({"query": args.terms, "matches": [dict(compact(p, mkt), score=s) for s, p in scored[:args.limit]],
             "note": "Keyword match only. For a task description, read `list` and judge fit instead."})

    if args.cmd == "show":
        p = plugins.get(args.plugin)
        if not p:
            out({"error": f"no plugin '{args.plugin}'", "close": [x for x in plugins if args.plugin.lower() in x]}, 3)
        out(dict(p, install=f"/plugin install {p['name']}@{mkt}",
                 themes=[t["title"] for t in themes if p["name"] in t["plugins"]]))

    if args.cmd == "new":
        if not changelog:
            repo = cfg.get("repo")
            if not repo:
                out({"error": "no CHANGELOG.md available for this marketplace"}, 2)
            import subprocess
            r = subprocess.run(["gh", "api", f"repos/{repo}/commits?per_page={args.limit * 10}",
                                "--jq", "[.[] | {date: .commit.author.date[:10], message: (.commit.message | split(\"\\n\")[0])}]"],
                               capture_output=True, text=True, timeout=30)
            if r.returncode:
                out({"error": "no CHANGELOG.md and commit history unreachable", "detail": r.stderr.strip()[:200]}, 2)
            out({"marketplace": mkt, "source": f"commits of {repo}",
                 "note": "No CHANGELOG.md; these are the marketplace repo's recent commit subjects.",
                 "recent": json.loads(r.stdout)})
        sections = re.split(r"(?m)^### ", changelog)[1:]
        res = []
        for sec in sections[:args.limit]:
            head, _, body = sec.partition("\n")
            items = [re.sub(r"\s+", " ", b).strip() for b in re.split(r"(?m)^- ", body) if b.strip() and not b.startswith("#")]
            res.append({"heading": head.strip(), "items": [i.split("## ")[0][:400] for i in items]})
        out({"marketplace": mkt, "recent": res})

    if args.cmd == "check":
        unknown = {t["id"]: [x for x in t["plugins"] if x not in plugins] for t in themes}
        unknown = {k: v for k, v in unknown.items() if v}
        grouped = {x for t in themes for x in t["plugins"]}
        ungrouped = sorted(set(plugins) - grouped)
        out({"marketplace": mkt, "source": source, "plugins": len(plugins),
             "unknown_names_in_groups": unknown, "ungrouped": ungrouped,
             "ok": not unknown}, 0 if not unknown else 4)


if __name__ == "__main__":
    main()
