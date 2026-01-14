# Copyright 2026 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Statement Balance Report Eurbrl",
    "summary": """Info for EUR and BRL on statements andmonthly report""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "https://github.com/clementmbr/personal-finance",
    "depends": [
        "account_statement_balance_report",
        "account_statement_category",
    ],
    "data": [
        "views/account_bank_statement_line_views.xml",
        "views/account_journal_views.xml",
        "views/currency_rate_views.xml",
        "report/account_statement_balance_report.xml",
    ],
    "demo": [],
}
