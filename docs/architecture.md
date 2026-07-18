# Architecture

## Design goals

HausaQA keeps parsing separate from QA decisions. Adapters produce a shared `Segment`; independent checks produce immutable `Issue` objects; the engine aggregates those issues into a `Report`. This makes each rule testable without a file parser or CLI.

## Data flow

1. A thin adapter reads CSV, TSV, JSON, XLIFF 1.2, or XLIFF 2.0.
2. It emits `Segment(source, target, reference)` values.
3. `check_segments` runs placeholder, orthography, and optional terminology checks.
4. Each finding has category, stable code, MQM-style severity, message, and segment reference.
5. `Report` serializes to deterministic text or JSON.

## Placeholder engine

`placeholders.py` extracts token families with explicit regular expressions, compares multisets, then compares order. Syntax checks run independently so malformed target fragments are not silently treated as ordinary text.

Supported families are ICU named placeholders, typed ICU number/date/time placeholders, printf specifiers, mustache placeholders, XML/HTML tags, and generic bracketed inline tags. The engine intentionally does not attempt full ICU MessageFormat parsing in 0.1.0. Complex plural/select expressions should be added behind a parser with dedicated fixtures, not by broadening one regular expression.

Missing, extra, malformed, and corrupted tokens are critical. Reordering is major because some systems allow harmless movement while others attach meaning to order.

## Orthography engine

The orthography checker is deliberately conservative. Hausa meaning cannot be inferred from a bare letter alone, so the engine does not claim every `b`, `d`, `k`, or `y` should be hooked. It flags hooked-letter substitution only when source and target become equivalent after removing hooks. This is useful for same-language revision and normalization checks, but it will not find every hooked-letter omission in an English-to-Hausa translation.

Straight or curly apostrophes immediately before `y` are flagged in favor of modifier apostrophe `ʼ`. ASCII sequences such as `b'` before a letter are treated as likely fallback damage. Combining marks are surfaced for manual verification rather than automatically rewritten.

Mixed Latin and Arabic-script detection is a script-consistency signal, not a claim that Arabic-script Hausa is invalid. A segment containing both scripts may be intentional and should be reviewed in context. Capitalization detection only examines an unambiguous lowercase letter after terminal punctuation.

These uncertainties are intentional. Version 0.1.0 prefers explainable false negatives over speculative language correction.

## Terminology engine

Glossary checks activate only when a source term appears as a case-insensitive whole term. The target must contain the approved term, and forbidden variants are reported separately. Exact whole-term matching does not perform Hausa morphological analysis, so an inflected form can be flagged even when linguistically valid. Projects should list accepted forms explicitly until morphology-aware matching is introduced.

## Adapters

Adapters contain no QA policy. XLIFF parsing uses the standard library, supports versions 1.2 and 2.0, and preserves inline element shape. It does not resolve external entities, schemas, or remote resources.

## Compatibility and extension points

Stable public concepts in 0.1.0 are `Segment`, `Issue`, `Severity`, `Report`, check functions, and the `hausaqa check` CLI. New checks should return issues rather than print or exit. New adapters should only return segments. This prevents format-specific logic from leaking into the engine.
