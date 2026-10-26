# Fixes from the Sound Comparisons author's feedback

## TL;DR
The author of SoundComparisons.com raised four points. Each has a small fix:
1. Dots for words a variety does not have (e.g. Quechua "seven" in Inkawasi). The data marks these with the transcription `..`; the original site skips them, we did not. Skip them in the build.
2. A list of recordings that fail to play. The original server already checks its disk and returns no sound file when one is missing, so the build can write that list without downloading anything. Write it to a local `missing-recordings.csv`, sent to the author by hand.
3. A full-screen button, so the browser bars go away on phones.
4. Aymara and Uru colours look alike. Colours were spread by region order, so neighbouring regions got neighbouring hues. Assign colours so regions that are close on the map get clearly different colours.

## Steps
- [x] Build: drop variants whose transcription is `--`, `..`, `...` or `…` (same rule as the original site's `Transcription.js`). Drop the variety for that word when nothing is left.
- [x] Build: write `missing-recordings.csv`: one row per transcription that has a real transcription but no sound file on the server, with study, variety, word and the expected file name.
- [x] Keep the CSV out of the repo (gitignored); it is sent to the author by hand.
- [x] Build: compute one colour per region per study. Greedy: each region takes the colour from a 24-colour set that is furthest (CIELAB distance) from the colours of regions within 300 km. Template reads the colours from the data.
- [x] Template: full-screen button, shown only where the browser supports it (not iPhone Safari). Add home-screen app meta tags so iPhone users can get a bar-free view via "Add to Home Screen".
- [x] Verify in a browser: Inkawasi "seven" has no dot; colours; full-screen button.

## Review
- Andes "six" and "seven": Inkawasi no longer listed or shown on the map. 306 Andes entries dropped in total, plus about 170 elsewhere (same `..` markers).
- Colours: the closest pair of regions within 150 km now differs by at least 51 CIELAB units in every study (before: 7 to 12 in Europe and Andes). Around Titicaca: Southern Aymara blue, Uru yellow, Peru South red, Bolivia green, Chipaya magenta.
- Report: 814 rows. 771 single missing files in varieties that have other recordings (Andes 321, Romance 235, Celtic 110, ...), and 43 varieties with no files at all. Most of those are historical, but the Europe study's six Donegal varieties (Glencolumbkille, Glenties, Gweedore-Carrick, Loughanure, Teelin, Tory Island) have none, which points to folder names.
- Full screen: the button shows in desktop Chrome. Entering full screen needs a real tap, which browser automation cannot give, so it was not tested end to end. To be checked on an Android phone.
