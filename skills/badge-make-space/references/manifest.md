# Cleanup manifest

The helper operates only on `/Users/antonioperedo/Desktop/badges`. Inventorying or applying from another current directory does not expand that scope. It never follows links, and it never edits badge content. Apply is for an explicitly requested repository cleanup, after the agent has inspected the current model index and dependencies described in the skill.

`inventory` writes relative filenames, sizes and modification times, plus separate working and Git totals. It does not hash every file or nominate deletions. Build the keep index yourself from current evidence, then fingerprint each protected file and each proposed removal with `fingerprint(path)` from the helper. A fingerprint contains `path`, `bytes`, `mtime_ns` and `sha256`.

The manifest is a JSON object:

```json
{
  "version": 1,
  "root": "/Users/antonioperedo/Desktop/badges",
  "authorization": "Owner requested cleanup of obsolete badge files in this repository",
  "models": [
    {
      "badge": "the actual badge name",
      "blender": "the actual current relative Blender path",
      "export": "the actual current relative USDZ path",
      "evidence": "the selection record and dependency checks used"
    }
  ],
  "keep": [],
  "remove": []
}
```

Replace the example model entry with the actual current model index. `keep` must be nonempty and include fingerprint objects for the retained editable files, exports and required resources. `remove` contains fingerprint objects with an additional nonempty `reason` field. The agent supplies real inspected paths and hashes, not these placeholders. A file may not occur in both lists. No directories or wildcard patterns are accepted.

Only known generated artifact and cache extensions are accepted for removal. Source, Markdown, JSON, project configuration, the skill collection, agent settings and Git are protected. Old text metadata can remain; it is small compared with repeated models and images. If a different cleanup needs source deletion, use a separately reviewed action rather than weakening this helper.

The apply receipt must be a new path inside the repository. It records the planned paths before deletion and each actual deletion immediately after it, with hashes and reasons. A changed file, linked path, missing fingerprint or protected path fails the full preflight before any deletion. A later concurrent change or write error aborts the operation; inspect its receipt and make a fresh plan for the remaining files. Never blindly rerun a partially applied manifest.

The helper proves file identity and scope. It does not prove that the selected latest versions are correct or that their dependencies are complete. Those decisions remain the agent's responsibility.
