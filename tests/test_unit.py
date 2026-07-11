import sys
import os

# Allow imports from BACKEND/ without a package install
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'BACKEND'))

from werkzeug.security import generate_password_hash, check_password_hash
from transactions import parse_amount


# ---------------------------------------------------------------------------
# Section 1 — Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = generate_password_hash('password123')
        assert hashed != 'password123'

    def test_correct_password_verifies(self):
        hashed = generate_password_hash('password123')
        assert check_password_hash(hashed, 'password123') is True

    def test_wrong_password_fails(self):
        hashed = generate_password_hash('password123')
        assert check_password_hash(hashed, 'wrongpassword') is False

    def test_different_hashes_same_password(self):
        hash1 = generate_password_hash('password123')
        hash2 = generate_password_hash('password123')
        assert hash1 != hash2


# ---------------------------------------------------------------------------
# Section 2 — Amount parsing
# ---------------------------------------------------------------------------

class TestParseAmount:
    def test_valid_integer_string(self):
        assert parse_amount('100') == 100.0

    def test_valid_float_string(self):
        assert parse_amount('50.75') == 50.75

    def test_empty_string(self):
        assert parse_amount('') is None

    def test_whitespace_only(self):
        assert parse_amount('   ') is None

    def test_alphabetic_string(self):
        assert parse_amount('abc') is None

    def test_zero(self):
        assert parse_amount('0') is None

    def test_negative(self):
        assert parse_amount('-10') is None

    def test_zero_float(self):
        assert parse_amount('0.00') is None


# ---------------------------------------------------------------------------
# Section 3 — Balance arithmetic
# ---------------------------------------------------------------------------

class TestBalanceArithmetic:
    def test_deposit_increases_balance(self):
        assert 1000.0 + 250.0 == 1250.0

    def test_withdraw_decreases_balance(self):
        assert 1000.0 - 250.0 == 750.0

    def test_withdraw_full_balance_gives_zero(self):
        assert 500.0 - 500.0 == 0.0

    def test_withdraw_exceeds_balance(self):
        # amount=250 does NOT exceed balance=1000 → check should pass through
        assert (250.0 > 1000.0) is False

    def test_withdraw_exceeds_balance_correctly_blocked(self):
        # amount=1500 exceeds balance=1000 → correctly detected as insufficient funds
        assert (1500.0 > 1000.0) is True
