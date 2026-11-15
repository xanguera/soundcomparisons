# Variety pages, meaning groups, compare, sound search, links back

## TL;DR
Today the site works one way only: pick a word, hear it across all varieties. This adds five features from the original site, sized for a phone:
1. **Variety page.** Tap the info button for the selected variety to open a sheet with where it is spoken, what kind of speech it is, who spoke, recorded and transcribed it, links (Wikipedia, Glottolog, the original site), and all its words to play one by one or in a row.
2. **Meaning groups.** The word picker is split into the original's groups (Numbers, Colours, Body...), with chips at the top to jump. Previous/next follow the same order.
3. **Compare.** From a variety page, add it to a compare set (2 to 6 varieties). The map and list then show only those varieties. "Play all" plays them for this word and then moves on to the next word.
4. **Search by sound or spelling.** The word search also matches the second reference gloss (e.g. Spanish in Andes) and local spellings. A "Sounds" switch searches the transcriptions instead, with a row of the study's IPA symbols to tap, since phones cannot type them.
5. **Links back.** "Open on SoundComparisons.com" for the current word and for each variety.

Local spellings (e.g. Quechua orthography) are also shown under the transcription where the data has them.

All of this data is already in what the build downloads; the build just drops it today.

## Data (build.py)
Per study, add:
- `words[i]` gets two more fields: the original's word key (`FileNameRfcModernLg01`, for links) and the second gloss (`FullRfcModernLg02`, only when it differs from the first).
- `groups`: `[[name, [word indices]]]`, in the global meaning-group order, words ordered by `MeaningGroupMemberIx`. Words in no group go in a last "Other" group.
- `cells`: variants become triplets `[ipa, path, spelling]` (spelling = `SpellingAltv1`, '' when none).
- `info[li]`: per variety, only non-empty fields: long name/tooltip, status description (from the global status types), historical period, locality (precise locality, nearest city, state/region), ISO code, Glottocode, Wikipedia link, speaker name, and credits as resolved names (spoken by, recorded by, transcription, sound editing, reconstruction, citations "Author Year: pages"). Plus the original's variety key (`FilePathPart`) for links.
- Watch the page size: today 3.9 MB raw. Report before and after, raw and gzipped.

## Page (template.html)
- `variants()` reads triplets. List rows show the spelling in small type after the transcription when present.
- Now bar: an info button, shown when a variety is selected, opens its variety page.
- Variety page (sheet, like About): header with name and region dot; details; links; credits; "Add to compare" toggle; "Play all words"; list of words (gloss, IPA, spelling, play). Tapping a word plays it. A link per word to jump to that word on the map.
- Compare: a slim bar under the word bar, "Comparing 3: A, B, C · Clear", shown only in compare mode. Compare set is per study, kept in localStorage, max 6. The word view filters rows to the set. "Play all" in compare mode continues across words ("Play all words"); Stop stops it.
- Word picker: group chips at top (scroll to group); sections with group headers. Search box with a Words / Sounds switch. Words: gloss, second gloss, proto form, local spellings. Sounds: any transcription of that word contains the query; the result shows how many varieties match. IPA symbol row (non-ASCII letters used in the study, most frequent first) inserts into the box.
- Prev/next and swipe step through the group order. URLs keep the word number, so old links still work.
- Links back: `https://soundcomparisons.com/#/en/<study>/map/<word key>/` in the list header; `https://soundcomparisons.com/#/en/<study>/language/<FilePathPart>` on the variety page.

## Steps
- [x] Build: words extra fields, groups, spelling triplets, info. Rebuild, report size.
- [x] Page: triplets + spelling display.
- [x] Page: variety page sheet + info button.
- [x] Page: meaning groups in picker, group order for prev/next.
- [x] Page: sound/spelling search with IPA symbol row.
- [x] Page: compare set, filtered view, play across words.
- [x] Page: links back.
- [x] About text: mention the new features briefly.
- [x] Verify in browser (desktop and narrow): each feature, light and dark; Escape closes sheets; old `#Study/N` links still open the same word.
- [x] Check links back open the right word/variety on the original site (2 to 3 samples).
- [x] Code review, commit, push, watch deploy.
- [x] Desktop: sheets sit over the sidebar instead of covering the whole window (added during testing).

## Out of scope
- Cognate colouring (data has cognate IDs for some words; separate decision).

## Review
- Page data: 3.9 MB to 4.4 MB raw (about 610 KB gzipped in total). The missing-recordings report is unchanged (814 rows).
- Every word sits in exactly one group in all nine studies.
- Variety page: details, credits, links and the full word list show for proto-languages and living varieties. Play all words and the per-word Map button work; Map jumps to the word with the variety selected.
- Compare: one variety shows a "add one more" hint; two or more filter the map and list. Play all words moved from word 1 to "three" by itself within 10 s. The compare set is kept per study.
- Sounds search: typing ʎ in Andes lists the words that contain it with match counts; the list then marks ʎ in each transcription. Letters come first in the symbol row, diacritics after.
- Spellings: shown on their own line under the transcription.
- Links back: Andes word "four" (key "cuatro"), Germanic "hundred", Chipaya Aransaya and Standard Catalan (Palma) all open the right word or variety on soundcomparisons.com.
- Phone width tested in a 390 px frame (the browser window would not resize): the now bar fits with the extra button; the variety page reads well.
- Old `#Study/N` links still open the same word (word numbers did not change). No console errors.
- Not checked: dark theme visually (all new styles use the theme colours).
- Code review found 10 issues, all fixed: Wikipedia links with a #section, diacritic search missing precomposed letters (now NFD), case mismatch between count and highlight, Map button silent for a variety outside the comparison, hover cutting into the variety page's Play all, full redraw on every keystroke, slow search, variety page left open across a study change, two cleanups. Re-tested in the browser after the fixes.
- Known data quirk: two Mapudungun words share the key "solamente", so both link to the same word on the original site.
