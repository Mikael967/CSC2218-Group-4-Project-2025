

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone
import uuid
from enum import Enum


# Add the root directory of the project to the Python path
sys.path.append(str(Path(__file__).resolve().parents[3]))
from banking_system import AccountStatus, AccountType, SavingsAccount, CheckingAccount, Account
from domain_layer import InterestStrategy, LimitConstraint, CheckingInterestStrategy,SavingsInterestStrategy

@pytest.fixture
def savings_interest_strategy() -> InterestStrategy:
    return SavingsInterestStrategy(annual_rate=0.05)

@pytest.fixture
def checking_interest_strategy() -> InterestStrategy:
    return CheckingInterestStrategy()

@pytest.fixture
def limit_constraint() -> LimitConstraint:
    return LimitConstraint(daily_limit=500.0, monthly_limit=1500.0)


@pytest.fixture
def savings_account(savings_interest_strategy) -> SavingsAccount:
    """Fixture to create a default SavingsAccount with no transaction limits for testing."""
    return SavingsAccount(account_type=AccountType.SAVINGS,initial_balance=1500.0,interest_strategy=savings_interest_strategy,limit_constraint=None)

@pytest.fixture
def checking_account(checking_interest_strategy) -> CheckingAccount:
    """Fixture to create a default CheckingAccount with no transaction limits for testing."""
    return CheckingAccount(account_type=AccountType.CHECKING,initial_balance=1500.0,interest_strategy=checking_interest_strategy,limit_constraint=None)

# --- Test Account Initialization ---

def test_account_initialization_defaults():
    """Test basic account initialization with default balance."""
    account = CheckingAccount(account_type=AccountType.CHECKING) # Use concrete class
    assert isinstance(account.account_id, str)
    assert len(str(uuid.UUID(account.account_id))) == 36 # Check if it's a valid UUID string
    assert account.account_type == AccountType.CHECKING
    assert account.balance == 5.0
    assert account.status == AccountStatus.ACTIVE
    assert isinstance(account.creation_date, datetime)


def test_account_initialization_with_balance():
    """Test account initialization with a specific positive balance."""
    account = SavingsAccount(account_type=AccountType.SAVINGS, initial_balance=150.50)
    assert account.balance == 150.50
    assert account.account_type == AccountType.SAVINGS
    

def test_account_initialization_negative_balance():
    """Test that initializing with a negative balance raises ValueError."""
    with pytest.raises(ValueError, match="Initial balance cannot be negative."):
        CheckingAccount(account_type=AccountType.CHECKING, initial_balance=-100.0)

# --- Test Account Methods ---

def test_deposit_positive_amount(checking_account):
    """Test depositing a positive amount increases balance."""
    initial_balance = checking_account.balance
    deposit_amount = 100.0
    checking_account.deposit(deposit_amount)
    assert checking_account.balance == initial_balance + deposit_amount

def test_deposit_zero_amount(checking_account):
    """Test that depositing zero raises ValueError."""
    with pytest.raises(ValueError, match="Deposit amount must be positive."):
        checking_account.deposit(0.0)

def test_deposit_negative_amount(checking_account):
    """Test that depositing a negative amount raises ValueError."""
    with pytest.raises(ValueError, match="Deposit amount must be positive."):
        checking_account.deposit(-50.0)

def test_close_account(checking_account):
    """Test closing an account changes its status."""
    assert checking_account.is_active()
    checking_account.close_account()
    assert checking_account.status == AccountStatus.CLOSED
    assert not checking_account.is_active()

def test_is_active(checking_account):
    """Test the is_active method."""
    assert checking_account.is_active()
    checking_account.status = AccountStatus.CLOSED
    assert not checking_account.is_active()

def test_account_repr(checking_account):
    """Test the string representation of an account."""
    representation = repr(checking_account)
    assert f"id={checking_account.account_id}" in representation
    assert f"type={checking_account.account_type.value}" in representation
    assert f"balance={checking_account.balance:.2f}" in representation
    assert f"status={checking_account.status.value}" in representation
    assert f"created={checking_account.creation_date.isoformat()}" in representation

# --- Test SavingsAccount Specifics ---

def test_savings_withdraw_success(savings_account):
    """Test successful withdrawal within limits."""
    initial_balance = savings_account.balance
    withdraw_amount = 100.0
    savings_account.withdraw(withdraw_amount)
    assert savings_account.balance == initial_balance - withdraw_amount

def test_savings_withdraw_to_minimum_balance(savings_account):
    """Test withdrawal exactly down to the minimum balance."""
    withdraw_amount = savings_account.balance - SavingsAccount.MINIMUM_BALANCE
    savings_account.withdraw(withdraw_amount)
    assert savings_account.balance == SavingsAccount.MINIMUM_BALANCE

def test_savings_withdraw_below_minimum(savings_account):
    """Test withdrawal that would go below the minimum balance."""
    withdraw_amount = savings_account.balance - SavingsAccount.MINIMUM_BALANCE + 1.0
    with pytest.raises(ValueError, match="minimum balance requirement not met"):
        savings_account.withdraw(withdraw_amount)
    assert savings_account.balance == 1500.0 # Balance should remain unchanged

def test_savings_withdraw_negative_amount(savings_account):
    """Test withdrawing a negative amount from SavingsAccount."""
    with pytest.raises(ValueError, match="withdraw amount must be positive."):
        savings_account.withdraw(-50.0)

def test_savings_withdraw_zero_amount(savings_account):
    """Test withdrawing zero amount from SavingsAccount."""
    with pytest.raises(ValueError, match="withdraw amount must be positive."):
        savings_account.withdraw(0.0)

def test_savings_withdraw_from_closed_account(savings_account):
    """Test withdrawing from a closed SavingsAccount."""
    savings_account.close_account()
    with pytest.raises(ValueError, match="Cannot withdraw from a closed account."):
        savings_account.withdraw(50.0)

# --- Test CheckingAccount Specifics ---

def test_checking_withdraw_success(checking_account):
    """Test successful withdrawal."""
    initial_balance = checking_account.balance
    withdraw_amount = 100.0
    checking_account.withdraw(withdraw_amount)
    assert checking_account.balance == initial_balance - withdraw_amount

def test_checking_withdraw_exact_balance(checking_account):
    """Test withdrawing the entire balance."""
    withdraw_amount = checking_account.balance
    checking_account.withdraw(withdraw_amount)
    assert checking_account.balance == 0.0

def test_checking_withdraw_insufficient_funds(checking_account):
    """Test withdraw with insufficient funds."""
    withdraw_amount = checking_account.balance + 1.0
    with pytest.raises(ValueError, match="Insufficient funds for withdraw."):
        checking_account.withdraw(withdraw_amount)
    assert checking_account.balance == 1500.0 # Balance should remain unchanged

def test_checking_withdraw_negative_amount(checking_account):
    """Test withdrawing a negative amount from CheckingAccount."""
    with pytest.raises(ValueError, match="withdraw amount must be positive."):
        checking_account.withdraw(-50.0)

def test_checking_withdraw_zero_amount(checking_account):
    """Test withdrawing zero amount from CheckingAccount."""
    with pytest.raises(ValueError, match="withdraw amount must be positive."):
        checking_account.withdraw(0.0)

def test_checking_withdraw_from_closed_account(checking_account):
    """Test withdrawing from a closed CheckingAccount."""
    checking_account.close_account()
    with pytest.raises(ValueError, match="Cannot withdraw from a closed account."):
        checking_account.withdraw(50.0)

# --- Test CheckingAccount Getters ---

def test_checking_get_balance(checking_account):
    """Test the get_balance method."""
    assert checking_account.get_balance() == 1500.0
    checking_account.deposit(50.0)
    assert checking_account.get_balance() == 1550.0

def test_checking_get_status(checking_account):
    """Test the get_status method."""
    assert checking_account.get_status() == AccountStatus.ACTIVE
    checking_account.close_account()
    assert checking_account.get_status() == AccountStatus.CLOSED

def test_checking_get_account_type(checking_account):
    """Test the get_account_type method."""
    assert checking_account.get_account_type() == AccountType.CHECKING

def test_checking_get_creation_date(checking_account):
    """Test the get_creation_date method."""
    assert isinstance(checking_account.get_creation_date(), datetime)
    assert checking_account.get_creation_date() == checking_account.creation_date



# --- Test account transfers ---
def test_transfer_success(savings_account:Account, checking_account:Account):
    """Test successful transfer between accounts."""
    initial_savings_balance = savings_account.balance
    initial_checking_balance = checking_account.balance
    transfer_amount = 100.0

    transaction = savings_account.transfer(transfer_amount, checking_account)
    
    assert transaction.amount == transfer_amount
    assert transaction.account_id == savings_account.account_id
    assert transaction.destination_account_id == checking_account.account_id

    assert savings_account.balance == initial_savings_balance - transfer_amount
    assert checking_account.balance == initial_checking_balance + transfer_amount
    assert transaction.timestamp <= datetime.now()  # Check if the timestamp is in the past

def test_exceeding_daily_limit(savings_account,limit_constraint):
    savings_account.limit_constraint = limit_constraint
    savings_account.withdraw(400)
    with pytest.raises(ValueError, match="Daily transaction limit exceeded."):
        savings_account.withdraw(200)

def test_exceeding_monthly_limit(savings_account,limit_constraint):
    may_1 = datetime(2025,5,1)
    may_2 = datetime(2025,5,2)

    #day 1
    limit_constraint = LimitConstraint(monthly_limit=1000, daily_limit=500, now_provider=make_now_provider(may_1))
    savings_account.limit_constraint = limit_constraint
    savings_account.withdraw(500)
    
    #day 2
    limit_constraint.now_provider = make_now_provider(may_2)
    savings_account.withdraw(400)
    with pytest.raises(ValueError):
        savings_account.withdraw(200)

#helper for monthly limit test
def make_now_provider(fixed_datetime):
    return lambda: fixed_datetime

def test_interest_implementation(savings_account):
    pass

def test_statement_generation(checking_account):
    pass