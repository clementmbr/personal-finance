# Copyright 2026 Akretion France (http://www.akretion.com/)
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    category_id = fields.Many2one(
        comodel_name="bank.statement.line.category",
        string="Category",
        domain="[('parent_id', '=', False)]",
        compute="_compute_category_id",
        readonly=False,
        store=True,
    )
    category_background_color = fields.Char(related="category_id.background_color")
    category_text_color = fields.Char(related="category_id.text_color")
    subcategory_id = fields.Many2one(
        comodel_name="bank.statement.line.category",
        string="Sub-Category",
        domain="[('parent_id', '=', category_id)]",
    )
    category_type = fields.Selection(related="category_id.category_type", store=True)
    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account")

    @api.depends("subcategory_id")
    def _compute_category_id(self):
        for line in self:
            line.category_id = line.subcategory_id.parent_id
