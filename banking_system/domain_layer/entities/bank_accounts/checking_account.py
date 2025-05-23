from datetime import datetime
from banking_system.domain_layer.entities.bank_accounts.account import Account, AccountType
from banking_system.domain_layer.entities.bank_accounts.account import AccountStatus


class CheckingAccount(Account):
    
    def get_balance(self) -> float:
        """Returns the current balance of the account."""
        return self.balance

    def get_status(self) -> AccountStatus:
        """Returns the current status of the account."""
        return self.status

    def get_account_type(self) -> AccountType:
        """Returns the type of the account."""
        return self.account_type

    def get_creation_date(self) -> datetime:
        """Returns the creation date of the account."""
        return self.creation_date
    
    