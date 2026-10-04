# Sound Comparisons: unofficial mobile view

> **This is not the Sound Comparisons website.** It is an unofficial, mobile-friendly interface to [SoundComparisons.com](https://soundcomparisons.com), created by Paul Heggarty and colleagues. All recordings, transcriptions and language data belong to the Sound Comparisons project. This repository only rewrites the user interface so the site's content is easier to use on a phone. It is not made, endorsed or maintained by the Sound Comparisons team.

## About Sound Comparisons

[Sound Comparisons](https://soundcomparisons.com) is a research database of recorded pronunciations of the same set of words across hundreds of languages, dialects and accents, grouped by language family (Germanic, Romance, Slavic, Celtic, Andean, Mapudungun and more). Its recordings were made in fieldwork campaigns and phonetically transcribed by its contributors. The project was founded by Paul Heggarty; its original source code is at [lingdb/Sound-Comparisons](https://github.com/lingdb/Sound-Comparisons).

If you use this material, please cite the original work, not this repository:

> Heggarty, P., Shimelman, A., Abete, G., Anderson, C., Sadowsky, S., Paschen, L., Maguire, W., Jocz, L., Aninao, M. J., Wägerle, L., Dërmaku-Appelganz, D., do Couto e Silva, A. P., Lawyer, L. C., Cabral, A. S. A. C., Walworth, M., Michalsky, J., Koile, E., Runge, J. & Bibiko, H.-J. (2019). Sound Comparisons: A new resource for exploring phonetic diversity across language families of the world. In S. Calhoun, P. Escudero, M. Tabain & P. Warren (eds.), *Proceedings of the 19th International Congress of Phonetic Sciences*, Melbourne, Australia, 280–284.

## Why this exists

The original site is a desktop application. On a phone its layout does not adapt to the screen, and it relies on hovering the mouse over the map to play sounds, which touch screens cannot do. This interface shows the same content in a phone-sized layout:

- choose a language family, then a word (swipe, arrows or search);
- tap a point on the map or a row in the list to hear that variety, with its IPA transcription;
- "Play all" plays every variety in order.

## How it works

1. **`build.py`** downloads the study data that the original site itself loads, from `https://soundcomparisons.com/query/data`. It keeps only the fields this page displays (variety names, coordinates, regions, words, transcriptions, audio file paths) and embeds them in `index.html`. All 9 studies shrink from about 80 MB to about 4 MB.
2. **`index.html`** is one static page (a Leaflet map plus a list). **Recordings are not copied into this repository**: each one plays directly from `soundcomparisons.com/sound/...`.
3. A **GitHub Action** (`.github/workflows/update-data.yml`) reruns `build.py` every Monday and commits `index.html` only if Sound Comparisons has changed its data. It can also be started by hand from the Actions tab.

The transcriptions, names and locations are shown as published by Sound Comparisons; this interface does not edit them.

## Files

| File | Purpose |
|---|---|
| `index.html` | The built page. Serve it from any static host (GitHub Pages works). |
| `template.html` | Page source; `__DATA__` is replaced by the build. |
| `build.py` | Fetches the data and writes `index.html`. Python 3 standard library only. |
| `.github/workflows/update-data.yml` | Weekly automatic refresh. |
| `LICENSE` | Licence terms (CC BY-NC-ND 4.0, following Sound Comparisons). |

To rebuild by hand: `python3 build.py`

To publish: Settings → Pages → *Deploy from a branch* → `main`, `/ (root)`.

## Licence

This repository follows the licence of the original Sound Comparisons project: **[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)** (Attribution, NonCommercial, NoDerivatives). In practice:

- **Attribution:** keep the credit to Sound Comparisons (Paul Heggarty et al.) visible wherever this page is shown.
- **NonCommercial:** do not use this page or its data for commercial purposes.
- **NoDerivatives:** do not modify the recordings or transcriptions or present altered versions of them.

See [`LICENSE`](LICENSE) for details and the full licence text.

## Being a good guest

Audio streams from the Sound Comparisons server, so every play uses their bandwidth. Please do not run automated bulk downloads through this page. If you plan to share it widely, consider letting the Sound Comparisons team know.

## Third-party components

[Leaflet](https://leafletjs.com) (BSD-2-Clause); fonts Charis SIL and Instrument Sans from Google Fonts (SIL Open Font License); map tiles © Esri, with OpenStreetMap data © OpenStreetMap contributors.
