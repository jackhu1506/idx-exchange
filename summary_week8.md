# Week 8 – Tableau Export Preparation

_Source: `src/week8_tableau.py`. Inputs `data/sold_flagged.csv` (448,036 × 98)
and `data/listings_flagged.csv` (607,299 × 87). Outputs 41 columns each._

## Outputs (local only)

`tableau_sold.csv` (448,036 × 41), `tableau_listings.csv` (607,299 × 41).
Derived from the week 7 flagged datasets; not committed.

## Purpose

The week 7 flagged datasets remain canonical. These exports are derived
consumers for Tableau only: trimmed to dashboard columns, with grouping keys
and format fixes Tableau requires. No rows dropped.

## Transformations

| Step | Sold | Listings |
|---|--:|--:|
| PostalCode → 5-digit | 448,032 valid (4 null) | 607,244 valid (55 null) |
| ListYrMo added | 100.0% | 100.0% |
| Emails backfilled within name | 72,451 | 105,136 |
| AgentKey by email | 440,849 (98.4%) | 597,964 (98.5%) |
| AgentKey by name fallback | 7,187 | 9,335 |
| OfficeKey | 17,885 of 19,161 | 20,066 of 21,514 |
| ratio_implausible_flag | 684 (0.153%) | 225 (0.129% of ratioed rows) |

`ListYrMo` is added because `YrMo` derives from `CloseDate` and is null for
anything unclosed — new-listing counts need their own month key.

## Open items resolved

- **`StandardStatus` absent from both feeds; use `MlsStatus`.** Values are the
  RESO enumeration (Active, Closed, Pending, ActiveUnderContract, ComingSoon).
  Sold is 100% Closed, so the week 6 status fallback was harmless.
- **No listing-agent identifier exists.** Verified against all 98 columns:
  `ListingKey`/`ListingId` are per-listing, `ListAgentAOR` is a regional
  association, `BuyerAgentMlsId` is the buyer side. Email is the only
  per-agent stable field.

## Agent keying

**Why not names.** 79,017 distinct emails share only 74,540 distinct names, so
~4,478 agents sit inside someone else's name. Shared names sum two agents'
sales into one row, and inflated rows are exactly what a top-100-by-volume
chart surfaces. Email is one-per-agent, so the key is a 12-char hash of it —
raw emails stay out of the output, names remain as display labels.

**Why backfill first.** 36% of names have an email on some listings and blank
on others. Hashing before filling splits those agents in two, halving their
volume. So each name's known email is copied onto its blank rows first, then
hashed. Recovered 72,451 sold rows (82% → 98.4% keyed) while distinct agents
moved by one, confirming it matched existing agents rather than inventing them.
Tradeoff: where a name is genuinely two people and only one has an email, both
sets of listings go to that one.

**Did it matter.** Top 100 by volume, name-grouped vs. key-grouped: 88 of 100
overlap. The twelve differences are genuine splitting (Gunderman 116/$176M +
102/$146M; Stanaland 43/$203M + 7/$34M — ranking only when combined),
displacement at the cutoff (Smith, Westfall, correctly grouped but pushed out),
and one data error (Valdez, $970,000,000 for $970,000). Neither method is
clean: names merge different agents, emails split the same one.


## `OriginalListPrice` data quality

`PriceRatio` p99 is 1.28, but 762 rows exceed 2. Three failure modes, all
passing the week 6 guard because it only excluded denominators ≤ 0:

| Mode | Rows | Example |
|---|--:|---|
| Dropped order of magnitude | ~301 | OLP 139,900 vs ListPrice 1,399,000 |
| Placeholder value | tens | OLP = 1 |
| Gross entry error | 1 | Close 970,000,000 vs list 974,777 |

The dropped-magnitude group is confirmed by digit signature, not inferred:
`249,888`/`2,499,888`, `143,800`/`1,428,000`. Losing a trailing zero divides by
exactly 10, hence the tight 9.5–9.8 cluster. Flagged at >5 rather than nulled,
per weeks 4–7: `ClosePrice` is correct on most of these, so the sale still
counts toward volume and median dashboards. The 2–5 band (78 rows) is left
unflagged as ambiguous. Valdez was already caught by week 7's
`ClosePrice_outlier_flag`.

## Feed relationship

Listings carries 175,719 closed rows against sold's 448,036 — ~39% coverage, so
these are separate extracts, not subset and superset. Closed metrics come from
sold only: listings would undercount by ~60%, and unioning double-counts.

## Limitations

- **Offices have no identifier.** `OfficeKey` is a normalized name (casefold,
  strip punctuation and Inc/LLC/Corp/Co) reducing 19,161 to 17,885 — the same
  approach disproven for agents above, unfixable with fields in this feed.
  Office rankings are approximate.
- The required close-to-original-list dashboard specifies an **average**, which
  is not robust to this tail even after flagging. Built as specified; median is
  the more defensible statistic.
- 95 sold / 101 listings rows have null agent names and cannot be keyed.
- 4 sold / 55 listings rows have no zip and will not appear in the heat maps.