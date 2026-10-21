---
name: browse
description: Browse what this plugin marketplace offers by theme — Israel & Hebrew, homelab, Linux desktop, Claude Code tooling, shopping, writing and more — read live from the published manifest. Use for "what plugins are there", "show me the marketplace", "what's in the homelab group", "where do I start".
---

# Browse the marketplace by group

The list is read live from the marketplace's published `marketplace.json`, so it is
current even when this plugin is not. Themed groups cut across the manifest's
categories; a plugin can sit in several.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/marketplace.py" groups              # themed groups + manifest categories, with counts
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/marketplace.py" group <id-or-title> # e.g. israel-hebrew, homelab, "Linux Sysadmin"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/marketplace.py" show <plugin>       # one plugin in full, with its install line
```

All output is JSON. If it carries a `warning`, the live manifest was unreachable and
the local copy was used instead. Pass the warning on to the user.

## Steps

1. With no specific ask, run `groups`. Present the themed groups (title, one-line
   description, count), lead with **Start here**, then mention that the categories
   also exist.
2. When the user picks a group, run `group` and list each plugin as name: what it
   does in one line. Put the install line at the end, not on every row.
3. For detail on one plugin, use `show`.
4. If `group` reports `missing_from_manifest`, the groups file names a plugin that
   is no longer published. Leave it out and mention `maintain-groups`.

Install line format: `/plugin install <name>@<marketplace>`. The user must have added
the marketplace once (`/plugin marketplace add <owner>/<repo>`).
