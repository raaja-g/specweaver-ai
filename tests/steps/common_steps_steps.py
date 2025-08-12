from pytest_bdd import given, when, then, parsers
print("[DEBUG] imported common_steps_steps")


@given(parsers.parse("{text}"))
def generic_given_step(text: str):
    pass


@when(parsers.parse("{text}"))
def generic_when_step(text: str):
    pass


@then(parsers.parse("{text}"))
def generic_then_step(text: str):
    pass


