# Marketplace Guide

**Start here** for the [`danielrosehill`](https://github.com/danielrosehill/Claude-Code-Plugins)
Claude Code plugin marketplace. It lets you browse about 180 plugins by theme, get
recommendations for a task, and see what's new, from inside Claude Code.

```
/plugin marketplace add danielrosehill/Claude-Code-Plugins
/plugin install marketplace-guide --marketplace danielrosehill/Claude-Code-Plugins
```

Then ask: *"what's in the marketplace?"*, *"is there a plugin for managing my
Synology?"*, *"what's new?"*

## Why it exists

Claude Code's `/plugin` browser searches only plugin names and descriptions, cut to
about 59 characters. It ignores categories and tags. This plugin reads the full
manifest and adds themed groups that cut across categories.

## Skills

| Skill | Use |
|---|---|
| `browse` | Themed groups and categories, then the plugins in each |
| `recommend` | Describe a task and get the plugins that fit, with install lines |
| `whats-new` | Recent additions from the marketplace changelog |
| `maintain-groups` | Maintainer: reconcile `groups.json` with the live manifest |

## Themed groups

Start here · Israel & Hebrew · Drive a website with your own browser · Shopping &
procurement · Claude Code tooling · Linux desktop (KDE) · Homelab & smart home ·
Writing & publishing · Audio, voice & transcription · Research · Personal life admin
· Privacy & security · Images, video & media · Data & datasets · Development & GitHub
· Hardware & maker

## How it stays current

The plugin list is never hard-coded. `scripts/marketplace.py` (Python standard
library only, JSON output) fetches the published `marketplace.json` each time it runs.
`groups.json` holds only group names and the plugins in each. Sources are tried in
this order:

1. `gh api` on the marketplace repo (freshest; needs `gh` auth, and is required for private marketplaces),
2. the raw GitHub URL (public only; GitHub's CDN can serve it up to ~5 minutes stale after a push),
3. Claude Code's local copy in `~/.claude/plugins/marketplaces/<name>/`, last, because
   it refreshes only on `/plugin marketplace update` and can lag behind. Output read
   from it carries a `warning`.

It works against another marketplace with `--marketplace <name> --url <raw manifest URL>`,
or `--manifest <path>`. Themed groups apply only to the marketplace named in
`groups.json`.

## License

MIT
