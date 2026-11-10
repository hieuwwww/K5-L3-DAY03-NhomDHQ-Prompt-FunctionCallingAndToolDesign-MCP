---
name: deduplicate
track: core
kind: local_formatter
requires_env: []
inputs: [items, strategy]
outputs: [items, original_count, unique_count, removed_count]
side_effect: false
---
# deduplicate

Removes duplicate research results without making a network request. URLs are
canonicalized by dropping fragments and common tracking parameters. The first
item is preserved when duplicate URLs or titles are found.
