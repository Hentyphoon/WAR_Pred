# Design

Direction for future UI work on WAR_pred. This describes where the UI should go; the app doesn't fully match it yet (see "Known gaps").

WAR_pred is a baseball reference tool. People come to look up a player and read numbers, so the numbers are the design.

## Hard rules

- No generic SaaS hero. No marketing headline, tagline, or call-to-action block.
- No gradient blobs, glows, mesh backgrounds, or glassmorphism.
- No random cards everywhere. Rows, rules, and spacing group data; a box needs a reason.
- No decoration just because there's empty space. Empty space stays empty.
- No stock illustrations, baseball clip art, or placeholder imagery.
- No emoji or icons standing in for labels.
- No KPI tile grids or dashboard chrome. This isn't an admin panel.
- No drop shadows or heavy rounded corners. Borders are 1px and radii stay at 4px or less.
- No animation beyond a short hover or focus transition (0.15s).
- No chart unless it shows something the table can't, such as a career arc against a projection.
- No filler copy like "Unlock insights" or "Powered by AI".

Test for any new element: if removing it loses no information and no function, remove it.

## Keep from the current UI

The Player page is the reference for the look. Extend it rather than replacing it.

| Element | Value |
|---|---|
| Page background | `#FCFCF2` |
| Text | `#14140F` |
| Secondary text | `#6E6C5E` |
| Rules and borders | `#DAD5C4` |
| Accent (actions, errors) | `#A3302B` |
| Headings, years | Georgia, regular weight |
| Numbers | Monospace with `tabular-nums` |
| Stat labels | Small, uppercase, letter-spaced |
| Content width | 640px centered column |

The red dashed "stitch" divider is the one deliberate flourish. It stays as a section divider on player-level pages. Don't add a second motif.

## Showing data

- Season data is a list of ruled rows, with columns that line up from row to row.
- Align numbers so they compare down a column. Don't vary precision within a column.
- Show missing values as `—`, never `NaN`, `null`, or `0`.
- Keep rate stats in baseball convention: `.312`, with no leading zero.
- Spell out or explain abbreviations like wRAA, BsR, and RLR somewhere on the page, for readers who don't know them.

## Showing predictions

- Offensive WAR is the headline number, with wRAA, BsR, and RLR as its components.
- Always say which season is predicted and which seasons it's based on.
- Keep predictions visually distinct from recorded stats, so a projection is never mistaken for a real result.
- Say what the prediction leaves out: this is offensive WAR, with no fielding.
- When a player has no prediction, say why in one plain sentence. Pre-1961 players stay fully viewable.

## Live games page (planned)

- `/live` lists today's games as ruled rows. `/live/:gamePk` shows one game's score, inning, current at-bat, and play-by-play.
- Text and numbers only: no animated diamond, pulsing "LIVE" badge, or scoreboard graphic. The hard rules still apply.
- Newest play first, in the same ruled-row style as season data.
- Show when the data last updated, and say so plainly if it has gone stale.
- Mark a revised play with a short text note rather than silently changing it.
- When no games are on, say so in one plain sentence.

## Known gaps

To address in the UI update:

- Search and Error pages don't share the Player page's type or layout: both use absolute positioning and a 4rem `nowrap` title that will overflow on phones.
- The Error button is unstyled, and the page says "Invalid player name" for every failure, including network errors.
- Colors are hard-coded in each stylesheet. Move them to `:root` tokens.
- `.stat`, `.stat-label`, and `.back-btn` are duplicated across `Player.css` and `predictions.css`.
- Stat labels at `0.65rem` are too small to read comfortably.
- The Predictions page has no player name, so it doesn't say whose numbers it's showing.
- The browser tab title is still `war-pred`.
