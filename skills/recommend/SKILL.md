---
name: recommend
description: Recommend plugins from this marketplace for a task the user describes ("I want to manage my Synology", "something for Hebrew emails", "help me buy a laptop in Israel") — reads the live manifest, judges fit, and gives install lines. Use when the user asks "is there a plugin for X" or "which plugin should I use".
---

# Recommend plugins for a task

Claude Code's `/plugin` browser searches names and descriptions only, and cuts
descriptions to about 59 characters. This skill reads the full manifest and judges fit.

## Steps

1. Read the whole catalogue once (about 180 entries, compact):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/marketplace.py" list
   ```
   For a quick keyword pass, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/marketplace.py" search <terms...>` ranks by name, tags,
   group and description. It is keyword-only, so use it to shortlist, not to decide.
2. Choose 1–3 plugins whose descriptions actually cover the task. Prefer a specific
   plugin over a general one. If the user's context implies a region or language
   (Israel, Hebrew), check the `israel-hebrew` group too.
3. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/marketplace.py" show <name>` on each pick to confirm.
4. Answer with, for each: the name, why it fits in one sentence, and the install line.
   If nothing fits, say so plainly and name the closest group instead of stretching
   a weak match.
