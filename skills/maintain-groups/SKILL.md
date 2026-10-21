---
name: maintain-groups
description: Maintainer task for this plugin — reconcile groups.json with the live marketplace manifest, add newly published plugins to themed groups, remove dead names, then commit and push. Use after adding plugins to the marketplace, or when browse reports missing_from_manifest.
---

# Maintain the themed groups

Run from a clone of this plugin's repo, not from the installed copy.

```bash
python3 scripts/marketplace.py check
```

- `unknown_names_in_groups` (exit code 4): the groups name plugins that are not
  published. Remove them. A plugin that was renamed should be replaced with its new
  name, not just removed.
- `ungrouped`: published plugins that are in no themed group. This is information,
  not an error, because every plugin is still reachable by category. Add a plugin to
  a group when it clearly belongs. Create a new group only when at least about 5
  plugins share a theme that no category expresses.

Group rules: ids are kebab-case; titles are short and human; the description is one
line; plugins may sit in several groups; keep **Start here** to at most about 6.

Then:
```bash
python3 -m json.tool groups.json > /dev/null && python3 scripts/marketplace.py check
git commit -am "groups: <what changed>" && git push
```
Bump `version` in `.claude-plugin/plugin.json` (patch) so installed copies update.
