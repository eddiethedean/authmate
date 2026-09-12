from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from authmate import ResourceRef, validate_action


@given(st.one_of(st.just(" x"), st.just("x "), st.just("\n"), st.just("\t")))
def test_action_rejects_control_or_outer_whitespace(value: str) -> None:
    try:
        validate_action(value)
    except (ValidationError, TypeError):
        return
    raise AssertionError("invalid action was accepted")


@given(
    st.text(
        alphabet=st.characters(whitelist_categories=("L", "N", "P", "S")), min_size=1, max_size=20
    )
)
def test_resource_ids_round_trip_exactly(value: str) -> None:
    if value != value.strip() or any(ord(char) < 32 or ord(char) == 127 for char in value):
        return
    resource = ResourceRef(type="report.document", id=value)
    assert resource.id == value
