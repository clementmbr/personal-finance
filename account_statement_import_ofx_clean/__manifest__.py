# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).
{
    "name": "OFX Import Cleaner",
    "version": "18.0.1.1.2",
    "category": "Accounting",
    "summary": "Fix OFX issues (empty FITID or duplicated IDs with distinct amounts)",
    "author": "Akretion",
    "website": "https://github.com/clementmbr/personal-finance",
    "license": "AGPL-3",
    "depends": ["account_statement_import_ofx"],
    "data": [
        "views/account_journal_views.xml",
    ],
    "installable": True,
}
