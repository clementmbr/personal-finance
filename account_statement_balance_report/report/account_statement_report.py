# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).


from odoo import fields, models
from odoo.tools import SQL


class AccountStatementReport(models.Model):
    _name = "account.statement.balance.report"
    _description = "Propagated Monthly Balance Report"
    _auto = False

    date = fields.Date(string="Month", readonly=True)
    journal_id = fields.Many2one("account.journal", readonly=True)
    company_id = fields.Many2one("res.company", readonly=True)
    currency_id = fields.Many2one("res.currency", readonly=True)

    balance = fields.Monetary(
        string="Balance (Journal)", currency_field="currency_id", aggregator="sum"
    )

    @property
    def _table_query(self) -> SQL:
        return SQL("%s %s %s", self._select(), self._from(), self._join())

    def _select(self) -> SQL:
        return SQL(
            """
            SELECT
                ROW_NUMBER() OVER () as id,
                grid.date, grid.journal_id, grid.company_id, grid.currency_id,
                COALESCE(vals.b, 0) as balance,
            """
        )

    def _from(self) -> SQL:
        return SQL(
            """
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
        """
        )

    def _join(self) -> SQL:
        return SQL(
            """
            LEFT JOIN LATERAL (
                SELECT st_line.running_balance  as b
                FROM account_bank_statement_line st_line
                JOIN account_move move ON move.id = st_line.move_id
                WHERE move.journal_id = grid.journal_id
                      AND move.date <= grid.date
                ORDER BY move.date DESC, st_line.internal_index DESC
                LIMIT 1
            ) vals ON TRUE
            """
        )
