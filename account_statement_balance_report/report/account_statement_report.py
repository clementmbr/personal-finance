# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).


from odoo import models, fields
from odoo.tools import SQL


class AccountStatementReport(models.Model):
    _name = "account.statement.balance.report"
    _description = "Propagated Monthly Balance Report"
    _auto = False

    date = fields.Date(string="Month", readonly=True)
    journal_id = fields.Many2one("account.journal", readonly=True)
    company_id = fields.Many2one("res.company", readonly=True)
    currency_id = fields.Many2one("res.currency", readonly=True)
    currency_eur_id = fields.Many2one("res.currency", readonly=True)
    currency_brl_id = fields.Many2one("res.currency", readonly=True)

    balance = fields.Monetary(
        string="Balance (Journal)", currency_field="currency_id", aggregator="sum"
    )
    balance_eur = fields.Monetary(
        string="Balance (EUR)", currency_field="currency_eur_id", aggregator="sum"
    )
    balance_brl = fields.Monetary(
        string="Balance (BRL)", currency_field="currency_brl_id", aggregator="sum"
    )
    rate_brl_eur = fields.Float(string="Rate BRL/EUR", digits=(12, 6), aggregator="avg")

    @property
    def _table_query(self) -> SQL:
        return SQL(
            """
            SELECT 
                ROW_NUMBER() OVER () as id,
                grid.date, grid.journal_id, grid.company_id, grid.currency_id,
                (SELECT id FROM res_currency WHERE name = 'EUR' LIMIT 1) 
                    as currency_eur_id,
                (SELECT id FROM res_currency WHERE name = 'BRL' LIMIT 1) 
                    as currency_brl_id,
                COALESCE(vals.b, 0) as balance,
                COALESCE(vals.b / NULLIF(%(r_j)s, 0) * %(r_e)s, 0) as balance_eur,
                COALESCE(vals.b / NULLIF(%(r_j)s, 0) * %(r_b)s, 0) as balance_brl,
                NULLIF(%(r_e)s, 0) / NULLIF(%(r_b)s, 0) as rate_brl_eur
            FROM (
                SELECT 
                    (date_trunc('month', d) + interval '1 month - 1 day')::date 
                        as date, 
                    j.id as journal_id, j.currency_id, j.company_id
                FROM generate_series(
                    CURRENT_DATE - interval '2 years', 
                    CURRENT_DATE, '1 month'
                ) d
                CROSS JOIN account_journal j WHERE j.type = 'bank'
            ) grid
            LEFT JOIN LATERAL (
                SELECT running_balance as b FROM account_bank_statement_line 
                WHERE journal_id = grid.journal_id AND date <= grid.date
                ORDER BY date DESC, internal_index DESC LIMIT 1
            ) vals ON TRUE
        """,
            r_j=self._get_rate_sql("grid.currency_id"),
            r_e=self._get_rate_sql("'EUR'"),
            r_b=self._get_rate_sql("'BRL'"),
        )

    def _get_rate_sql(self, curr) -> SQL:
        return SQL(
            f"(SELECT r.rate FROM res_currency_rate r "
            f"JOIN res_currency c ON r.currency_id = c.id "
            f"WHERE (c.id::text = {curr} OR c.name = {curr}) "
            f"AND r.company_id = grid.company_id "
            f"AND r.name <= grid.date ORDER BY r.name DESC LIMIT 1)"
        )
