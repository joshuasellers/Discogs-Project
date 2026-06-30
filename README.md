# Discogs-Project

Automate adding vinyl records to your Discogs collection by reverse-image-searching album art (Google Lens via SerpAPI) and matching results to Discogs releases.

## Setup

1. Create a `tokens.py` file in the project root (gitignored):

```python
discogs_token = "your_discogs_user_token"
serpapi_key = "your_serpapi_key"
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add album cover images to the `albums/` folder on GitHub (or update `helper.get_album_links()` for your image source).

## Workflow

The script uses `collection_draft.json` as a manifest you can edit by hand or via the interactive review step.

### Commands

| Command | Description |
|---------|-------------|
| `python discogstest.py match` | Scrape album images, run Google Lens, match Discogs releases, write manifest |
| `python discogstest.py review` | Interactively confirm, skip, change releases, or set media/sleeve grades |
| `python discogstest.py upload` | Add confirmed items to your Discogs collection with condition fields |
| `python discogstest.py run` | Run match → review → upload in one shot |

### Manifest format

`collection_draft.json` is created by `match` and updated by `review` and `upload`:

```json
{
  "defaults": {
    "media_condition": "Near Mint (NM or M-)",
    "sleeve_condition": "Near Mint (NM or M-)",
    "folder_id": 1
  },
  "items": [
    {
      "image_url": "https://...",
      "google_title": "Artist - Album [r12345]",
      "release_id": 12345,
      "release_title": "Artist - Album",
      "media_condition": "Very Good Plus (VG+)",
      "sleeve_condition": "Very Good (VG)",
      "notes": "",
      "status": "pending"
    }
  ]
}
```

**Status values:** `pending` → `confirmed` or `skipped` (via review) → `uploaded` (after upload).

You can edit the JSON directly between steps: change `release_id`, set `status` to `skipped`, or adjust `media_condition` / `sleeve_condition` using Discogs API values (e.g. `Mint (M)`, `Near Mint (NM or M-)`).

Uploads go to the folder specified in `defaults.folder_id` (default `1` = Uncategorized). Media and sleeve grades are set via your account's collection note fields after each release is added.

## TODOs

- test larger batch
