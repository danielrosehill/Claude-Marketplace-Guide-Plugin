---
name: whats-new
description: Show recent additions and changes to this plugin marketplace, from its CHANGELOG. Use for "what's new in the marketplace", "any new plugins", "what changed recently".
---

# What's new

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/marketplace.py" new --limit 3      # the three most recent dated changelog sections
```

Summarise each section as plugin name: what it does, one line each, newest first.
Include install lines for added plugins. If the output reports no changelog, say the
marketplace does not publish one and fall back to `browse`.
