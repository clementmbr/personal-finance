# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Monthly Statement Balance Report",
    "version": "1.0",
    "category": "Accounting/Reporting",
    "summary": "Monthly bank balances in EUR and BRL",
    "author": "Akretion",
    "website": "https://github.com/clementmbr/personal-finance",
    "depends": ["account_statement_category"],
    "data": [
        "security/ir.model.access.csv",
        "report/account_statement_report_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}
