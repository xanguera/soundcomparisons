# Sound Comparisons Pocket

A mobile-first front-end for [Sound Comparisons](https://soundcomparisons.com), the database of recorded pronunciations across language families by Paul Heggarty and colleagues.

Pick a family, pick a word, and tap any point on the map (or any row in the list) to hear how it is pronounced there, with its IPA transcription. "Play all" runs through every variety in turn.

## How it works

The original site is a desktop Backbone.js app that downloads 5–16 MB of JSON per language family and relies on mouse hover. Its JSON API (`/query/data`) sends no CORS headers, so it cannot be called from another site's browser page. The recordings themselves are plain MP3 files, which any page can play.

So this project:

1. **`build.py`** fetches every study from `https://soundcomparisons.com/query/data`, keeps only what the page needs (variety names, coordinates, regions, words, IPA, audio paths) and inlines it into `index.html`. All 9 studies shrink from about 80 MB to about 4 MB (about 0.5 MB gzipped).
2. **`index.html`** is a single static page (Leaflet map + list) that streams each recording directly from `soundcomparisons.com/sound/...`. No recordings are copied.

## Files

| File | Purpose |
|---|---|
| `index.html` | The built page. Serve it from any static host (GitHub Pages works). |
| `template.html` | Page source; `__DATA__` is replaced by the build. |
| `build.py` | Fetches live data and writes `index.html`. Python 3 standard library only. |

## Refreshing the data

```sh
python3 build.py
```

Run it whenever Sound Comparisons publishes new data, then commit the new `index.html`.

## Hosting on GitHub Pages

Settings → Pages → Source: *Deploy from a branch* → Branch: `main`, folder `/ (root)`.

## Notes

- Opening `index.html` straight from a file works in most browsers, but a hosted copy is more reliable on phones.
- Map tiles: Esri World Light/Dark Gray Canvas. Fonts: Charis SIL (designed for IPA) and Instrument Sans, from Google Fonts.
- Deep links: `index.html#Romance/12` opens word 12 of the Romance study.

## Credits

All recordings, transcriptions and language data belong to the Sound Comparisons project (Paul Heggarty et al.); see <https://soundcomparisons.com>. Audio is streamed from their server, so please credit them and be considerate with traffic if you share this widely.
