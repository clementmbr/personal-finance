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
    rate_brl_eur = fields.Float(string="Rate BRL/EUR", digits=(12, 6), aggregator="avg")

    def _select(self) -> SQL:
        select_base = super()._select()
        extension = SQL(
            """
            (SELECT id FROM res_currency WHERE name = 'EUR' LIMIT 1) as currency_eur_id,
            (SELECT id FROM res_currency WHERE name = 'BRL' LIMIT 1) as currency_brl_id,
            COALESCE(vals.b / NULLIF(%(r_j)s, 0) * %(r_e)s, 0) as balance_eur,
            COALESCE(vals.b / NULLIF(%(r_j)s, 0) * %(r_b)s, 0) as balance_brl,
            NULLIF(%(r_e)s, 0) / NULLIF(%(r_b)s, 0) as rate_brl_eur
            """,
            r_j=self._get_rate_sql_for_column("grid", "currency_id"),
            r_e=self._get_rate_sql_for_value("EUR"),
            r_b=self._get_rate_sql_for_value("BRL"),
        )
        return SQL("%s%s", select_base, extension)

    def _get_rate_sql_for_column(self, table, column) -> SQL:
        return SQL(
            """
            (SELECT r.rate FROM res_currency_rate r
             JOIN res_currency c ON r.currency_id = c.id
             WHERE c.id = %s
               AND r.company_id = grid.company_id
               AND r.name <= grid.date ORDER BY r.name DESC LIMIT 1)
        """,
            SQL.identifier(table, column),
        )

    def _get_rate_sql_for_value(self, currency_name) -> SQL:
        return SQL(
            """
            (SELECT r.rate FROM res_currency_rate r
             JOIN res_currency c ON r.currency_id = c.id
             WHERE c.name = %s
               AND r.company_id = grid.company_id
               AND r.name <= grid.date ORDER BY r.name DESC LIMIT 1)
        """,
            currency_name,
        )
