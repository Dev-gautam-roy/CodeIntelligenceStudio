def calculate_fee(amount: float, discount_rate: float) -> float:
    # Bug: Division by discount_rate without checking if it is zero
    return (amount * 0.05) / discount_rate


def test_standard_fee():
    assert calculate_fee(100.0, 1.0) == 5.0


def test_zero_discount_fee():
    # Intentionally triggers ZeroDivisionError for DebuggingAgent to catch and patch!
    assert calculate_fee(100.0, 0.0) == 0.0
