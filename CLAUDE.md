# marketplace-guide: notes for agents

Discovery plugin for the public `danielrosehill` marketplace. A private sibling,
`marketplace-guide-private` (repo `Claude-Marketplace-Guide-Private`), covers
`danielrosehill-private` with the **same** `scripts/marketplace.py`. Change the
script here first, then copy it there verbatim. Only `groups.json`, the README and
the plugin manifest differ.

- Never hard-code plugin lists or counts in skills or README prose. They come from
  the live manifest.
- After plugins are added to the marketplace: `python3 scripts/marketplace.py check`,
  then follow `skills/maintain-groups`.
- The local Claude Code marketplace clone can lag the published manifest. Verified
  2026-10-21: 172 local vs 178 published. That is why it is the last source tried.
