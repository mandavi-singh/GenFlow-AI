from genflow.tools import calculator


def test_calculator():
    assert calculator.invoke({"expression": "2 + 2 * 3"}) == "8"


def test_calculator_rejects_bad_input():
    assert calculator.invoke({"expression": "import os"}).startswith("error")
