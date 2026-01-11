from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    currency_eur_id = fields.Many2one(
        "res.currency", string="EUR", default=lambda self: self.env.ref("base.EUR").id
    )
    currency_brl_id = fields.Many2one(
        "res.currency", string="BRL", default=lambda self: self.env.ref("base.BRL").id
    )

    amount_eur = fields.Monetary(
        string="Amount (EUR)",
        compute="_compute_eurbrl",
        currency_field="currency_eur_id",
        store=True,
    )
    amount_brl = fields.Monetary(
        string="Amount (BRL)",
        compute="_compute_eurbrl",
        currency_field="currency_brl_id",
        store=True,
    )

    running_balance_eur = fields.Monetary(
        string="Running Balance (EUR)",
        compute="_compute_eurbrl",
        currency_field="currency_eur_id",
        store=True,
    )
    running_balance_brl = fields.Monetary(
        string="Running Balance (BRL)",
        compute="_compute_eurbrl",
        currency_field="currency_brl_id",
        store=True,
    )

    @api.depends("amount", "running_balance", "date", "currency_id")
    def _compute_eurbrl(self):
        eur = self.env.ref("base.EUR")
        brl = self.env.ref("base.BRL")
        for rec in self:
            rec.amount_eur = rec.currency_id._convert(
                rec.amount, eur, rec.company_id, rec.date
            )
            rec.amount_brl = rec.currency_id._convert(
                rec.amount, brl, rec.company_id, rec.date
            )
            rec.running_balance_eur = rec.currency_id._convert(
                rec.running_balance, eur, rec.company_id, rec.date
            )
            rec.running_balance_brl = rec.currency_id._convert(
                rec.running_balance, brl, rec.company_id, rec.date
            )
