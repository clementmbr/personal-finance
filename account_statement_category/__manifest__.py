# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Account Statement Category",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Personal finance categorization for bank statements",
    "author": "Akretion",
    "website": "https://github.com/clementmbr/personal-finance",
    "license": "LGPL-3",
    "depends": [
        "account",
        "account_statement_import_sheet_file",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/bank.statement.line.category.csv",
        "views/bank_statement_line_category_views.xml",
        "views/account_bank_statement_line_views.xml",
    ],
    "installable": True,
    "application": True,
}
