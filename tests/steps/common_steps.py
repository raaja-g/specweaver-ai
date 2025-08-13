import os
from pytest_bdd import given, when, then, parsers


# Enable generic catch-all steps ONLY when explicitly requested.
# This prevents tests from auto-passing without real step logic.
if os.getenv("ALLOW_GENERIC_STEPS", "0").lower() in {"1", "true", "yes"}:
    @given(parsers.re(r"^.+$"))
    def generic_given():
        pass

    @when(parsers.re(r"^.+$"))
    def generic_when():
        pass

    @then(parsers.re(r"^.+$"))
    def generic_then():
        pass
