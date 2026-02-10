# Copyright 2004-2020 Odoo S.A.
# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "OFX Import Cleaner",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Remove invalid OFX transactions (empty FITID) during import",
    "author": "Akretion",
    "website": "https://github.com/clementmbr/personal-finance",
    "license": "AGPL-3",
    "depends": ["account_statement_import_ofx"],
    "data": ["wizard/account_statement_import.xml"],
    "installable": True,
    "application": False,
}
