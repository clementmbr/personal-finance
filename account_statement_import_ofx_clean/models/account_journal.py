# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    ignore_empty_fitid = fields.Boolean(
        string="Ignore Empty FITID",
        help="If checked, in OFX import files, transactions without a FITID will "
        "be ignored.",
    )
    deduplicate_fitid_by_amount = fields.Boolean(
        string="Deduplicate FITID by Amount",
        help="If checked, in OFX import files, transactions with the same FITID but "
        "different amounts or different date will be treated as unique.",
    )
