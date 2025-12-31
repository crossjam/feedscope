# Feedscope CLI Documentation

Feedscope CLI provides commands to interact with the Feedbin API.

## Authentication

```bash
feedscope auth login
feedscope auth status
feedscope auth logout
```

## Entries

Retrieve and filter entries.

```bash
# List entries
feedscope entries list [--page N] [--since DATE] [--read/--no-read] [--starred]

# Show an entry
feedscope entries show <ENTRY_ID>

# List entries for a feed
feedscope entries feed <FEED_ID>
```

## Entry State

Manage unread, starred, and updated entries.

```bash
# Unread
feedscope unread list
feedscope unread mark-read <ID>...
feedscope unread mark-unread <ID>...

# Starred
feedscope starred list
feedscope starred star <ID>...
feedscope starred unstar <ID>...

# Updated
feedscope updated list [--include-diff]
feedscope updated mark-read <ID>...

# Recently Read
feedscope recently-read list
feedscope recently-read create <ID>...
```

## Saved Searches

```bash
feedscope saved-search list
feedscope saved-search get <ID> [--include-entries]
feedscope saved-search create --name "Name" --query "Query"
feedscope saved-search update <ID> [--name "Name"] [--query "Query"]
feedscope saved-search delete <ID>
```

## Tags & Taggings

```bash
# Tags
feedscope tags rename --old-name "Old" --new-name "New"
feedscope tags delete --name "Tag"

# Taggings
feedscope taggings list
feedscope taggings create --feed-id <ID> --name "Tag"
feedscope taggings delete <TAGGING_ID>
```

## Subscriptions

```bash
feedscope subscriptions list
feedscope subscriptions get <ID>...
feedscope subscriptions create <URL>
feedscope subscriptions update <ID> "New Title"
feedscope subscriptions delete <ID>
```

## Supporting Tools

```bash
# Imports (OPML)
feedscope imports list
feedscope imports create <OPML_FILE>
feedscope imports status <IMPORT_ID>

# Pages
feedscope pages save --url <URL>

# Icons
feedscope icons list

# Extract Content
feedscope extract <URL>
```

## Configuration

Configuration is stored in `~/.config/dev.pirateninja.feedscope/config.toml` (or platform equivalent).

To use the extraction service, add your API credentials to the config file:

```toml
[auth]
email = "..."
password = "..."

[extract]
username = "..."
secret = "..."
```
