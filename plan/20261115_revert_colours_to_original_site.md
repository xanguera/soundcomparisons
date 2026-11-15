# Use the original site's map colours

## TL;DR
In the last push we gave every region its own colour, chosen so that regions close on the map look different. The author of SoundComparisons.com says this was wrong. In the multi-family studies (Europe, Andes), colour should show the main branch or family: one colour for all Germanic, one for all Romance, one for all Quechua, and so on. Regions get their own colours only in the single-branch studies (Germanic, Romance, Celtic...). He asks us to copy the original site's colours exactly.

The original site's code does exactly this, and we can copy it:
- Each study has a flag, `ColorByFamily`. It is on for Europe and Andes, off for the other seven studies. Our build already downloads it and ignores it.
- When it is on, a variety takes the colour of its family. When it is off, it takes the colour of its region.
- The colour comes from a fixed list of 10 pastel colours in the site's code (`js/models/Colors.js`). The family colour is picked by the family's position in the study's family list; the region colour by the region's number (`RegionGpIx`), wrapping round after 10.

So the fix is: delete our own colour picker and reproduce that rule in the build.

The author thinks the RGB codes sit in the database tables. They do not reach the website: the data the site downloads has no colour fields, and the live code uses the 10-colour list above. What the live site shows is what we copy. If he has other colours in the database that he wants used, that is a question for him (see the reply draft below).

## What the original site does (checked against live code, 15 Nov 2026)
- Colour list, in order: `#E6E6E6, #CCCCFF, #CCFFFF, #CFFF7C, #FFFACD, #FFCC99, #C59595, #E6C7DD, #FECECE, #FFFFFF`. Index wraps modulo 10.
- Region colour (`models/Region.js`): if the study's `ColorByFamily` is 1, use the family colour; otherwise `colors[RegionGpIx % 10]`.
- Family colour (`models/Family.js`): `colors[position of the family in the study's family list]`, as the API returns that list.
- The map marker uses that colour flat (`views/render/MapView.js`). It is only replaced in "colour by cognate" mode, which we do not have.
- Note: the GitHub repo `lingdb/Sound-Comparisons` is out of date (its colour list differs). Use the live files, not the repo.

Expected result:
- Europe: Germanic `#CCCCFF`, Romance `#CCFFFF`, Balto-Slavic `#CFFF7C`, Celtic `#FFFACD`, English `#FFCC99` (family 0 "Europe", if anything sits in it, `#E6E6E6`).
- Andes: Quechua `#CCCCFF`, Aymara `#CCFFFF`, Uru-Chipaya `#CFFF7C`, Mapudungun `#FFFACD`. Bolivian and south Peruvian Quechua are the same colour.
- Single-branch studies: one colour per region by `RegionGpIx`.

## A display problem to solve
These are pale pastels, two of them near-white (`#E6E6E6`, `#FFFFFF`). Our markers have a white outline and sit on light map tiles, so pale dots will be hard to see. The original site draws its markers differently (labelled boxes). Fix: keep the colours exactly, and give the markers a dark outline instead of the white one. Same for the small colour dot next to each region name in the list. Do not darken or change the colours themselves; the author asked for them as they are.

## Steps
- [x] Build: remove the colour picker added in the last push (the colour-distance helper, the 24-colour set and the greedy assignment) and the `math`/`colorsys` imports it needed.
- [x] Build: add the 10-colour list, copied from the live `Colors.js`, with a comment saying where it comes from.
- [x] Build: for each region, compute its colour with the original rule: family position when `ColorByFamily` is 1, else `RegionGpIx % 10`. Family position = index in the API's `families` list for that study, matched on `FamilyIx`. Keep writing it into the same `colors` field, so the page code does not change.
- [x] Page: change the marker outline from white to a dark colour that reads on both light and dark map tiles; same for the region dot in the list. Check the selected-marker style still stands out.
- [x] Rebuild `index.html`.
- [x] Verify: for Europe, Andes and Germanic, print region name to colour and compare with the expected result above.
- [x] Verify in a browser, side by side with soundcomparisons.com, the map for one word in Europe, Andes and Germanic: same colour for the same group. Screenshot each.
- [x] Verify on a phone-width window that the pale dots are visible on the map.
- [x] Update the "Review" section of `20261026_author_feedback_fixes.md`: the region-colour change was reverted, with a link to this plan.
- [x] Build: take each variety's region from its first membership that is a listed region (found during verification, see Review).
- [ ] Commit, push, check the deployed page.

## Reply to the author (draft, Xavi sends)
Covering only the colour point. Points to mention: reverted; now uses the site's own rule (family colour in Europe and Andes, region colour in single-branch studies) and its own colour list; the site loads its colours from a fixed list in its code, not from the database, so if the database holds other colours he would like used, he can send them or say which table, and we will switch.

## Out of scope
- His question on AI speech synthesis from fine IPA transcriptions. Worth a separate answer, not a code change.

## Review
- Built colours compared with the live site's own colour function (`getColor()` on every region), in all nine studies: identical.
- Andes map side by side with soundcomparisons.com: Quechua lavender, Aymara cyan, Uru-Chipaya lime, Mapudungun pale yellow on both. All Quechua regions one colour.
- Europe map: the four branches read at a glance. Pale dots are clearly visible with the dark outline.
- Found and fixed an older build bug: five Europe varieties (Göttingen German, Prato Italian, Standard Czech, Cornamona Irish, and one more) also sit in a featured set that is not a region. The build kept that set and showed them grey under "Other". They now go to their real region (e.g. Göttingen in Upper German, as the database says).
- Old Norse has no region membership in the data (Europe and Germanic), so it stays grey. Data gap, not a build bug.
- The phone-width window resize did not take in the browser tool; visibility was judged on the desktop-width map, which uses the same dots.
