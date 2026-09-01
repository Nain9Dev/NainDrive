"""Unit tests for Spanish identity document validation.

Covers the checksum algorithm for DNI and NIE. Both are natural-person documents;
a driving school student is always a natural person, so corporate NIF is out of scope.

All document numbers used here are structurally valid but fictional.
"""
import pytest

from src.domain.identity import (
    InvalidIdentityDocument,
    normalise_identity_document,
    validate_identity_document,
)


class TestValidDocuments:
    """Documents whose control letter matches the modulo 23 checksum."""

    @pytest.mark.parametrize(
        "document",
        [
            "12345678Z",  # DNI
            "00000000T",  # DNI, lowest value
            "99999999R",  # DNI, highest value
            "X1234567L",  # NIE starting with X
            "Y1234567X",  # NIE starting with Y
            "Z1234567R",  # NIE starting with Z
        ],
    )
    def test_accepts_correct_checksum(self, document: str) -> None:
        assert validate_identity_document(document) == document

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("12345678z", "12345678Z"),
            ("  12345678Z  ", "12345678Z"),
            ("12345678-Z", "12345678Z"),
            ("x1234567l", "X1234567L"),
        ],
    )
    def test_normalises_case_whitespace_and_separators(self, raw: str, expected: str) -> None:
        assert normalise_identity_document(raw) == expected


class TestRejectedDocuments:
    """The previous implementation accepted every one of these."""

    @pytest.mark.parametrize(
        "document",
        [
            "AAAAA",       # alphanumeric but meaningless
            "12345678A",   # correct shape, wrong control letter
            "12345678",    # missing control letter
            "1234567Z",    # too few digits
            "123456789Z",  # too many digits
            "W1234567L",   # W is not a valid NIE prefix
            "X12345678L",  # NIE with too many digits
            "12345678I",   # I is excluded from the control alphabet
            "12345678O",   # O is excluded from the control alphabet
            "12345678U",   # U is excluded from the control alphabet
            "",
            "   ",
        ],
    )
    def test_rejects_invalid_document(self, document: str) -> None:
        with pytest.raises(InvalidIdentityDocument):
            validate_identity_document(document)


class TestControlAlphabet:
    """The letters I, O and U are deliberately absent from the checksum alphabet
    because they are visually confusable with 1, 0 and V."""

    @pytest.mark.parametrize("excluded", ["I", "O", "U"])
    def test_excluded_letters_never_produced(self, excluded: str) -> None:
        from src.domain.identity import CONTROL_LETTERS

        assert excluded not in CONTROL_LETTERS

    def test_control_alphabet_has_23_letters(self) -> None:
        from src.domain.identity import CONTROL_LETTERS

        assert len(CONTROL_LETTERS) == 23
