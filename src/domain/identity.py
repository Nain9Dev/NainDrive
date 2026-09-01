"""Spanish identity document validation.

`DNI` and `NIE` are the identity documents issued to natural persons in Spain. Both
carry a control letter derived from the numeric part modulo 23, which makes them
verifiable offline: a transcription error is caught at the point of entry rather than
surfacing later as an unmatched record.

Corporate `NIF` uses a different checksum and is out of scope: a driving school
student is always a natural person.
"""
import re
from typing import Final

# The control alphabet omits I, O and U. They are visually confusable with 1, 0 and V,
# which is precisely the class of transcription error the checksum exists to catch.
CONTROL_LETTERS: Final[str] = "TRWAGMYFPDXBNJZSQVHLCKE"

# A NIE replaces its leading letter with a digit before the checksum is applied.
NIE_PREFIX_VALUES: Final[dict[str, str]] = {"X": "0", "Y": "1", "Z": "2"}

_SEPARATORS = re.compile(r"[\s\-.]")
_DNI_SHAPE = re.compile(r"^(\d{8})([A-Z])$")
_NIE_SHAPE = re.compile(r"^([XYZ])(\d{7})([A-Z])$")


class InvalidIdentityDocument(ValueError):
    """Raised when a document is not a structurally valid DNI or NIE."""


def normalise_identity_document(raw: str) -> str:
    """Strips separators and whitespace, and upper-cases the result.

    Normalising before validating means `12345678-z` and `12345678Z` are the same
    document, which is how a person writes it versus how it is stored.
    """
    if raw is None:
        raise InvalidIdentityDocument("Identity document is required.")
    return _SEPARATORS.sub("", raw).strip().upper()


def _expected_control_letter(eight_digits: str) -> str:
    return CONTROL_LETTERS[int(eight_digits) % 23]


def validate_identity_document(raw: str) -> str:
    """Returns the normalised document, or raises if the checksum does not match.

    The returned value is always the canonical form: eight digits or a NIE prefix,
    followed by the upper-case control letter.
    """
    document = normalise_identity_document(raw)

    if not document:
        raise InvalidIdentityDocument("Identity document is required.")

    dni = _DNI_SHAPE.match(document)
    if dni:
        digits, control = dni.groups()
        expected = _expected_control_letter(digits)
        if control != expected:
            raise InvalidIdentityDocument(
                f"Control letter for DNI {digits} should be {expected}, not {control}."
            )
        return document

    nie = _NIE_SHAPE.match(document)
    if nie:
        prefix, digits, control = nie.groups()
        expected = _expected_control_letter(NIE_PREFIX_VALUES[prefix] + digits)
        if control != expected:
            raise InvalidIdentityDocument(
                f"Control letter for NIE {prefix}{digits} should be {expected}, not {control}."
            )
        return document

    raise InvalidIdentityDocument(
        f"'{document}' is not a valid DNI (8 digits plus letter) or NIE (X, Y or Z, "
        "7 digits plus letter)."
    )
