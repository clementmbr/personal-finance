# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    currency_eur_id = fields.Many2one(
        "res.currency", string="EUR", default=lambda self: self.env.ref("base.EUR").id
    )
    currency_brl_id = fields.Many2one(
        "res.currency", string="BRL", default=lambda self: self.env.ref("base.BRL").id
    )

    current_statement_balance_eur = fields.Monetary(
        string="Balance (EUR)",
        compute="_compute_eurbrl",
        currency_field="currency_eur_id",
        store=True,
    )
    current_statement_balance_brl = fields.Monetary(
        string="Balance (BRL)",
        compute="_compute_eurbrl",
        currency_field="currency_brl_id",
        store=True,
    )

    @api.depends("current_statement_balance", "currency_id")
    def _compute_eurbrl(self):
        eur = self.env.ref("base.EUR")
        brl = self.env.ref("base.BRL")
        today = fields.Date.today()
        for rec in self:
            rec.current_statement_balance_eur = rec.currency_id._convert(
                rec.current_statement_balance, eur, rec.company_id, today
            )
            rec.current_statement_balance_brl = rec.currency_id._convert(
                rec.current_statement_balance, brl, rec.company_id, today
            )

    def action_compute_journals_current_balance(self):  # pylint: disable=missing-return
        """Action to trigger EUR/BRL balance recomputation for selected journals."""
        super().action_compute_journals_current_balance()
        self._compute_eurbrl()
