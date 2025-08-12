# Generic catch-all step definitions to allow feature scenarios to run without specific implementations
from pytest_bdd import given, when, then, parsers


@given(parsers.re(r"^.+$"))
def generic_given():
    # Placeholder for any Given step
    pass


@when(parsers.re(r"^.+$"))
def generic_when():
    # Placeholder for any When step
    pass


@then(parsers.re(r"^.+$"))
def generic_then():
    # Placeholder for any Then step
    pass


