# ADR-0005 — Identity documents are verified by checksum

Status: Approved
Date: 2026-08-30

## Context

REQ-001 requires rejecting any identity document that is not a valid Spanish
`DNI` or `NIE`. The implementation checked `^[A-Z0-9]{5,12}$`, which accepts `AAAAA`
and `12345678A`, the latter having the wrong control letter.

The requirement was declared and not met. For a project whose stated purpose is to
demonstrate deterministic validation, this was the most damaging defect in the codebase:
it contradicted the claim it was meant to prove.

## Decision

Validate the control letter using the modulo 23 checksum, in a dedicated domain module
`src/domain/identity.py`.

- `DNI`: eight digits plus the control letter.
- `NIE`: prefix `X`, `Y` or `Z` mapped to `0`, `1` or `2`, then the same checksum.

Corporate `NIF` is deliberately out of scope: a driving school student is a natural
person. REQ-001 is corrected accordingly.

Input is normalised before validation, so `12345678-z` and `12345678Z` are the same
document.

## Consequences

- A transcription error is caught at entry instead of surfacing later as an unmatched
  record.
- Demonstration data had to be corrected: two of the four seeded students carried
  invalid documents, as did several test fixtures.
- Any document set imported in future must be checksum-valid, which is the point.

## Rejected alternatives

- **Validate shape only.** What the code did. Meets the letter of a badly written
  requirement and none of its intent.
- **Call an external verification service.** Unnecessary: the checksum is offline and
  deterministic, and an external dependency would add a failure mode for no gain.

## Reconsider when

The product accepts students holding non-Spanish documents, which needs a passport
policy rather than an extension of this one.
