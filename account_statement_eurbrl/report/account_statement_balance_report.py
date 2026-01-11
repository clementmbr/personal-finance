# Copyright 2026 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import SQL


class AccountStatementBalanceReport(models.Model):
    _inherit = "account.statement.balance.report"

    currency_eur_id = fields.Many2one("res.currency", readonly=True)
    currency_brl_id = fields.Many2one("res.currency", readonly=True)

    balance_eur = fields.Monetary(
        string="Balance (EUR)", currency_field="currency_eur_id", aggregator="sum"
    )
    balance_brl = fields.Monetary(
        string="Balance (BRL)", currency_field="currency_brl_id", aggregator="sum"
    )

    def _select(self) -> SQL:
        select_base = super()._select()
        return SQL(
            """
            %s
            vals.ce as currency_eur_id,
            vals.cb as currency_brl_id,
            COALESCE(vals.be, 0) as balance_eur,
            COALESCE(vals.bb, 0) as balance_brl
            """,
            select_base,
        )

    def _join(self) -> SQL:
        join_base = super()._join()
        new_code = join_base.code.replace(
            "st_line.running_balance  as b",
            """
                st_line.running_balance as b,
                st_line.running_balance_eur as be,
                st_line.running_balance_brl as bb,
                st_line.currency_eur_id as ce,
                st_line.currency_brl_id as cb
            """,
        )
        return SQL(new_code, *join_base.params)
